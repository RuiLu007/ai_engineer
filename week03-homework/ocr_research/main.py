"""
作业二: 为 LlamaIndex 构建 OCR 图像文本加载器
运行方式: cd week03-homework && uv run python -m ocr_research.main
"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv

# 加载 .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()


def test_ocr_reader():
    """测试 ImageOCRReader 的基本功能"""
    from ocr_research.image_ocr_reader import ImageOCRReader

    print("=" * 60, flush=True)
    print("Step 1: 测试 ImageOCRReader", flush=True)
    print("=" * 60, flush=True)

    reader = ImageOCRReader(lang="ch")
    test_dir = Path(__file__).parent / "test_images"
    image_files = sorted(str(f) for f in test_dir.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg"))

    print(f"\n找到 {len(image_files)} 张测试图片:", flush=True)
    for f in image_files:
        print(f"  - {os.path.basename(f)}", flush=True)

    # 加载所有图片
    documents = reader.load_data(image_files)

    print(f"\n成功生成 {len(documents)} 个 Document 对象", flush=True)

    # 打印每个 Document 的详情
    results = []
    for i, doc in enumerate(documents):
        print(f"\n{'─' * 50}", flush=True)
        print(f"Document {i + 1}: {doc.metadata['file_name']}", flush=True)
        print(f"  OCR 模型: {doc.metadata['ocr_model']}", flush=True)
        print(f"  语言: {doc.metadata['language']}", flush=True)
        print(f"  文本块数: {doc.metadata['num_text_blocks']}", flush=True)
        print(f"  平均置信度: {doc.metadata['avg_confidence']:.4f}", flush=True)
        print(f"  文本预览 (前 300 字):", flush=True)
        print(f"    {doc.text[:300]}", flush=True)
        print(f"\n  格式化文本 (前 5 块):", flush=True)
        for line in doc.metadata["formatted_text"].split("\n")[:5]:
            print(f"    {line}", flush=True)

        results.append({
            "file_name": doc.metadata["file_name"],
            "num_text_blocks": doc.metadata["num_text_blocks"],
            "avg_confidence": doc.metadata["avg_confidence"],
            "text_preview": doc.text[:200],
        })

    return documents, results


def test_batch_loading():
    """测试批量目录加载"""
    from ocr_research.image_ocr_reader import ImageOCRReader

    print("\n" + "=" * 60, flush=True)
    print("Step 2: 测试批量目录加载 (load_data_from_dir)", flush=True)
    print("=" * 60, flush=True)

    reader = ImageOCRReader(lang="ch")
    test_dir = Path(__file__).parent / "test_images"
    documents = reader.load_data_from_dir(str(test_dir))
    print(f"\n批量加载完成: {len(documents)} 个 Document", flush=True)
    return documents


def test_rag_integration(documents):
    """测试与 LlamaIndex RAG 系统的集成"""
    print("\n" + "=" * 60, flush=True)
    print("Step 3: 测试 LlamaIndex RAG 集成", flush=True)
    print("=" * 60, flush=True)

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("跳过 RAG 集成测试: 未设置 DASHSCOPE_API_KEY", flush=True)
        return

    from llama_index.core import Settings, VectorStoreIndex
    from llama_index.llms.openai_like import OpenAILike
    from llama_index.embeddings.dashscope import (
        DashScopeEmbedding,
        DashScopeTextEmbeddingModels,
    )

    # 配置 LLM 和 Embedding
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
    print("LLM 和 Embedding 模型配置完成", flush=True)

    # 构建索引
    print("正在构建向量索引...", flush=True)
    index = VectorStoreIndex.from_documents(documents)
    print("索引构建完成", flush=True)

    # 查询测试
    query_engine = index.as_query_engine(similarity_top_k=3)

    queries = [
        "图片中提到了什么航班信息？",
        "图片中有哪些系统配置信息？",
        "图片中提到了什么地名或位置？",
    ]

    for q in queries:
        print(f"\n问题: {q}", flush=True)
        response = query_engine.query(q)
        answer = str(response)
        print(f"回答: {answer[:300]}", flush=True)

        # 打印来源
        for j, node in enumerate(response.source_nodes[:2]):
            print(f"  来源 {j + 1}: {node.metadata.get('file_name', 'N/A')} "
                  f"(score: {node.score:.4f})", flush=True)


def main():
    print("=" * 60, flush=True)
    print("为 LlamaIndex 构建 OCR 图像文本加载器", flush=True)
    print("基于 PaddleOCR 的多模态数据接入", flush=True)
    print("=" * 60, flush=True)

    # Step 1: 测试 OCR Reader
    documents, results = test_ocr_reader()

    # Step 2: 测试批量加载
    batch_docs = test_batch_loading()

    # Step 3: RAG 集成
    test_rag_integration(documents)

    # 保存结果
    output_path = Path(__file__).parent / "ocr_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nOCR 结果已保存至: {output_path}", flush=True)
    print("\n实验完成!", flush=True)


if __name__ == "__main__":
    main()
