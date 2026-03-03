"""
多任务问答助手 - 主程序
基于 LangChain 构建的简化问答助手
"""

import sys
import os
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.qa_agent import create_qa_agent
from core.logger import app_logger
from config.settings import settings


def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("🤖 多任务问答助手")
    print("=" * 60)
    print("支持功能:")
    print("  💬 日常对话 - 例: '你好 ，AI 助手，你能为我做什么？'")
    print("  🌤️  天气查询 - 例: '查询北京天气'")
    print("  🔍 信息搜索 - 例: '搜索最新财经'")
    print()
    print("输入 'quit' 或 'exit' 退出程序")
    print("=" * 60)


def main():
    """主函数"""
    # 验证配置
    if not settings.validate_all():
        print("❌ 配置验证失败，请检查环境变量配置")
        return 1
    
    print_welcome()
    
    # 创建问答代理
    try:
        agent = create_qa_agent()
        print(f" 问答助手已启动 (会话ID: {agent.session_id})")
        print()
        
        while True:
            try:
                # 获取用户输入
                user_input = input(" 您: ").strip()
                
                # 检查退出命令
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("👋 再见！")
                    break
                
                if not user_input:
                    continue
                
                # 处理用户输入
                print(" 正在思考...")
                result = agent.chat(user_input)
                
                # 显示响应
                print(f" 助手: {result['response']}")
                
                # 显示使用的工具
                if result.get('tools_used'):
                    print(f"🔧 使用工具: {', '.join(result['tools_used'])}")
                
                # 测试缓存
                print(f"⏱️  处理时间: {result['processing_time_ms']:.1f}ms")
                print()
                
            except KeyboardInterrupt:
                print("\n 再见！")
                break
            except Exception as e:
                print(f"❌ 处理错误: {str(e)}")
                app_logger.error(f"处理用户输入时出错: {e}")
                continue
        
        # 结束会话
        agent.end_session()
        return 0
        
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        app_logger.error(f"程序启动失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())