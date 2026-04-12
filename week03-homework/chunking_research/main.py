"""
探索 LlamaIndex 中的句子切片检索及其参数影响分析
运行方式: cd week03-homework && uv run python -m chunking_research.main
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.core.node_parser import (
    SentenceSplitter,
    TokenTextSplitter,
    SentenceWindowNodeParser,
)
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.dashscope import (
    DashScopeEmbedding,
    DashScopeTextEmbeddingModels,
)


# ── 全局配置 ──────────────────────────────────────────────
def setup_llm_and_embedding():
    """配置 LLM 和嵌入模型（参照 project3_1 的设置）"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("请设置 DASHSCOPE_API_KEY 环境变量")

    Settings.llm = OpenAILike(
        model="qwen-plus",
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=api_key,
        is_chat_model=True,
    )

    Settings.embed_model = DashScopeEmbedding(
        model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3,
        embed_batch_size=6,
    )


# ── 加载文档 ──────────────────────────────────────────────
def load_documents() -> List[Document]:
    """从 docs/ 目录加载文档"""
    docs_dir = Path(__file__).parent / "docs"
    if not docs_dir.exists():
        raise FileNotFoundError(f"文档目录不存在: {docs_dir}")
    reader = SimpleDirectoryReader(input_dir=str(docs_dir))
    documents = reader.load_data()
    print(f"已加载 {len(documents)} 篇文档", flush=True)
    for doc in documents:
        print(f"  - {doc.metadata.get('file_name', 'unknown')}  ({len(doc.text)} 字)", flush=True)
    return documents


# ── 评估函数 ──────────────────────────────────────────────
def evaluate_splitter(
    splitter,
    documents: List[Document],
    question: str,
    ground_truth: str,
    splitter_name: str,
    is_sentence_window: bool = False,
) -> Dict[str, Any]:
    """
    使用给定的切片器构建索引、执行查询，并返回评估结果。
    """
    print(f"\n{'='*60}", flush=True)
    print(f"切片方式: {splitter_name}", flush=True)
    print(f"{'='*60}", flush=True)

    # 1. 切片
    t0 = time.time()
    nodes = splitter.get_nodes_from_documents(documents)
    split_time = time.time() - t0
    print(f"  切片数量: {len(nodes)}", flush=True)
    print(f"  切片耗时: {split_time:.2f}s", flush=True)

    # 打印前 3 个节点的长度信息
    for i, node in enumerate(nodes[:3]):
        print(f"  节点 {i}: {len(node.text)} 字", flush=True)

    # 2. 构建索引
    t0 = time.time()
    index = VectorStoreIndex(nodes)
    index_time = time.time() - t0
    print(f"  索引构建耗时: {index_time:.2f}s", flush=True)

    # 3. 查询
    t0 = time.time()
    if is_sentence_window:
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            node_postprocessors=[
                MetadataReplacementPostProcessor(target_metadata_key="window")
            ],
        )
    else:
        query_engine = index.as_query_engine(similarity_top_k=5)

    response = query_engine.query(question)
    query_time = time.time() - t0
    print(f"  查询耗时: {query_time:.2f}s", flush=True)

    # 4. 结果分析
    answer = str(response)
    source_texts = []
    for node in response.source_nodes:
        source_texts.append(node.text[:200])

    # 检查检索的上下文是否包含关键信息
    context_contains_answer = ground_truth in "".join(
        [n.text for n in response.source_nodes]
    )

    result = {
        "splitter_name": splitter_name,
        "num_chunks": len(nodes),
        "split_time": round(split_time, 2),
        "index_time": round(index_time, 2),
        "query_time": round(query_time, 2),
        "answer": answer,
        "context_contains_answer": context_contains_answer,
        "num_source_nodes": len(response.source_nodes),
        "source_preview": source_texts[:2],
    }

    print(f"\n  回答: {answer[:300]}...", flush=True)
    print(f"  上下文包含答案关键词: {context_contains_answer}", flush=True)

    return result


# ── 实验配置 ──────────────────────────────────────────────
EVAL_QUESTIONS = [
    {
        "question": "金融科技中人工智能在反欺诈领域的效果如何？",
        "ground_truth": "欺诈损失可降低约40%至60%",
    },
    {
        "question": "大语言模型的幻觉问题有哪些缓解方法？",
        "ground_truth": "检索增强生成",
    },
    {
        "question": "预测性维护能给工厂带来什么收益？",
        "ground_truth": "设备非计划停机时间减少了50%以上",
    },
]


def run_experiment_matrix(documents: List[Document]) -> List[Dict[str, Any]]:
    """执行完整的参数对比实验矩阵"""
    all_results = []

    # ── 实验 1: SentenceSplitter 不同参数组合 ──
    sentence_configs = [
        {"chunk_size": 256, "chunk_overlap": 0},
        {"chunk_size": 256, "chunk_overlap": 50},
        {"chunk_size": 256, "chunk_overlap": 128},
        {"chunk_size": 512, "chunk_overlap": 0},
        {"chunk_size": 512, "chunk_overlap": 50},
        {"chunk_size": 512, "chunk_overlap": 128},
        {"chunk_size": 1024, "chunk_overlap": 0},
        {"chunk_size": 1024, "chunk_overlap": 50},
        {"chunk_size": 1024, "chunk_overlap": 200},
    ]

    for cfg in sentence_configs:
        splitter = SentenceSplitter(
            chunk_size=cfg["chunk_size"],
            chunk_overlap=cfg["chunk_overlap"],
        )
        name = f"Sentence(size={cfg['chunk_size']}, overlap={cfg['chunk_overlap']})"
        for qa in EVAL_QUESTIONS:
            result = evaluate_splitter(
                splitter, documents, qa["question"], qa["ground_truth"], name
            )
            result["config"] = cfg
            result["question"] = qa["question"]
            all_results.append(result)

    # ── 实验 2: TokenTextSplitter 不同参数 ──
    token_configs = [
        {"chunk_size": 64, "chunk_overlap": 8},
        {"chunk_size": 128, "chunk_overlap": 16},
        {"chunk_size": 256, "chunk_overlap": 32},
    ]

    for cfg in token_configs:
        splitter = TokenTextSplitter(
            chunk_size=cfg["chunk_size"],
            chunk_overlap=cfg["chunk_overlap"],
            separator="\n",
        )
        name = f"Token(size={cfg['chunk_size']}, overlap={cfg['chunk_overlap']})"
        for qa in EVAL_QUESTIONS:
            result = evaluate_splitter(
                splitter, documents, qa["question"], qa["ground_truth"], name
            )
            result["config"] = cfg
            result["question"] = qa["question"]
            all_results.append(result)

    # ── 实验 3: SentenceWindowNodeParser 不同窗口大小 ──
    window_sizes = [1, 3, 5]

    for ws in window_sizes:
        splitter = SentenceWindowNodeParser.from_defaults(
            window_size=ws,
            window_metadata_key="window",
            original_text_metadata_key="original_text",
        )
        name = f"SentenceWindow(window={ws})"
        for qa in EVAL_QUESTIONS:
            result = evaluate_splitter(
                splitter,
                documents,
                qa["question"],
                qa["ground_truth"],
                name,
                is_sentence_window=True,
            )
            result["config"] = {"window_size": ws}
            result["question"] = qa["question"]
            all_results.append(result)

    return all_results


def generate_markdown_report(results: List[Dict[str, Any]]) -> str:
    """基于实验结果生成 Markdown 格式的对比表格"""
    lines = []
    lines.append("## 实验结果对比表\n")
    lines.append(
        "| 切片方式 | 问题 | 切片数 | 切片耗时(s) | 索引耗时(s) | 查询耗时(s) | 上下文包含答案 |"
    )
    lines.append("|---------|------|--------|-----------|-----------|-----------|-------------|")
    for r in results:
        q_short = r["question"][:15] + "..."
        lines.append(
            f"| {r['splitter_name']} | {q_short} | {r['num_chunks']} | "
            f"{r['split_time']} | {r['index_time']} | {r['query_time']} | "
            f"{'Y' if r['context_contains_answer'] else 'N'} |"
        )
    return "\n".join(lines)


def print_summary(results: List[Dict[str, Any]]):
    """打印实验总结"""
    print("\n" + "=" * 80, flush=True)
    print("实验总结", flush=True)
    print("=" * 80, flush=True)

    from collections import defaultdict
    grouped = defaultdict(list)
    for r in results:
        grouped[r["splitter_name"]].append(r)

    print(f"\n{'切片方式':<45} {'平均切片数':>8} {'答案命中率':>10} {'平均查询耗时':>12}", flush=True)
    print("-" * 80, flush=True)
    for name, group in grouped.items():
        avg_chunks = sum(r["num_chunks"] for r in group) / len(group)
        hit_rate = sum(1 for r in group if r["context_contains_answer"]) / len(group)
        avg_query = sum(r["query_time"] for r in group) / len(group)
        print(f"{name:<45} {avg_chunks:>8.0f} {hit_rate:>10.0%} {avg_query:>12.2f}s", flush=True)


def main():
    print("=" * 60, flush=True)
    print("LlamaIndex 句子切片检索参数影响分析实验", flush=True)
    print("=" * 60, flush=True)
    # flush=True 的作用是强制立即输出，不让内容在缓冲区里等待。

    # 1. 配置
    setup_llm_and_embedding()
    print("LLM 和嵌入模型配置完成", flush=True)

    # 2. 加载文档
    documents = load_documents()

    # 3. 运行实验
    results = run_experiment_matrix(documents)

    # 4. 打印总结
    print_summary(results)

    # 5. 生成对比表格并保存
    table_md = generate_markdown_report(results)
    print("\n" + table_md, flush=True)

    # 6. 保存完整结果到 JSON
    output_path = Path(__file__).parent / "results.json"
    serializable = []
    for r in results:
        s = dict(r)
        s.pop("source_preview", None)
        serializable.append(s)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
    print(f"\n完整结果已保存至: {output_path}", flush=True)

    # 7. 保存对比表格到 report 附录
    report_table_path = Path(__file__).parent / "experiment_table.md"
    with open(report_table_path, "w", encoding="utf-8") as f:
        f.write(table_md)
    print(f"对比表格已保存至: {report_table_path}", flush=True)


if __name__ == "__main__":
    main()
