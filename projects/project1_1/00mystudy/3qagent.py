import uuid
class QAAgent:
    """简化的问答代理，使用 LangChain 的 prompt | llm | output 语法"""
    
    def __init__(self, session_id: str = None):
        """初始化问答代理"""
        self.session_id = session_id or str(uuid.uuid4())
    
# 1. 不传入 session_id，自动生成唯一 ID
agent1 = QAAgent()
print(agent1.session_id)  # 输出类似：'550e8400-e29b-41d4-a716-446655440000'

# 2. 传入自定义 session_id，使用指定的值
agent2 = QAAgent(session_id="user_123456")
print(agent2.session_id)  # 输出：user_123456

# 693fc6b7-6e93-4fcf-8df0-b40d90538e03
# user_123456