
import os
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.dashscope import DashScopeEmbedding, DashScopeTextEmbeddingModels

# 增加调试日志
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger("llama_index").addHandler(logging.StreamHandler(stream=sys.stdout))
# 这个日志什么意思？code/p18log.ipynb
i=0
while i<3:
    try:
        api_key=os.getenv("DASHSCOPE_API_KEY")
        print(f"i={i},apikey = {api_key[:5]}*****")
        # break
    except Exception as e:
        print(f"i={i},error：{e}")
    i += 1
    from dotenv import load_dotenv
    load_dotenv()
# i=0,error：'NoneType' object is not subscriptable
# i=1,apikey = sk-19*****
# i=2,apikey = sk-19*****
Settings.llm = OpenAILike(
    model="qwen-plus",
    api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    is_chat_model=True
)

Settings.embed_model = DashScopeEmbedding(
    model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3,
    embed_batch_size=6,
    embed_input_length=8192
)

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("怎么休事假？")
print(response)
