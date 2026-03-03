from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.dashscope import DashScopeEmbedding, DashScopeTextEmbeddingModels

Settings.llm = OpenAILike(
    model = "qwen-plus",
    api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key = os.getenv("DASHSCOPE_API_KEY"),
    is_chat_model=True,
)

Settings.embed_model = DashScopeEmbedding(
   model_name = DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3, # 文本嵌入模型名称
   embed_batch_size = 6, # 批量大小，默认为6
   embed_input_length = 8192, # 输入长度，默认为8192
)

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("怎么休事假？")
print(response)
"""
None of PyTorch, TensorFlow >= 2.0, or Flax have been found. Models won't be available and only tokenizers, configuration and file/data utilities can be used.
2026-02-11 23:52:02,047 - INFO - HTTP Request: POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions "HTTP/1.1 200 OK"
休事假需按以下规定办理：

1. **申请方式**：须通过公司OA系统或书面填写《员工请假申请表》提交申请。  
2. **申请时间**：至少提前1个工作日提出申请；如遇突发情况，可事后补办手续，但应及时说明原因并尽快补交材料。  
3. **审批权限**：  
   - 3天以内（含）由直属主管审批；  
   - 3–7天由部门负责人审批；  
   - 7天以上需经人力资源部审核，并由分管领导审批。  
4. **工资待遇**：事假为无薪假，按实际缺勤天数扣发相应工资。  
5. **注意事项**：未经批准擅自离岗的，按旷工处理，将依据制度第十五条执行相应处罚。
"""