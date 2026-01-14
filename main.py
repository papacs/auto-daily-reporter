import uuid
from graph import graph
import os
from dotenv import load_dotenv

# 加载 .env
load_dotenv()

def main():
    # 模拟用户配置
    default_user = os.getenv("GITHUB_USER", "")
    default_repo = os.getenv("GITHUB_REPO", "")
    initial_state = {
        "github_username": default_user,
        "repo_name": default_repo,
        "user_feedback": ""
    }
    # 这里的 thread_id 是 LangGraph 用来区分“这是哪次任务”的
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("🏁 启动日报助手...")
    
    # 第一次运行：直到遇到 interrupt_before (也就是 review_node 之前停下)
    # 注意：LangGraph 的 interrupt 机制有点反直觉，它会在执行目标节点前停下
    # 所以我们得手动调整一下逻辑，或者简单点，让它跑到 review 后停下。
    # 这里为了演示方便，我们用简化的循环控制：
    
    current_inputs = initial_state
    
    # 1. 启动，跑到 review 处
    for event in graph.stream(current_inputs, config):
        pass # 让它自己跑完前面的节点

    while True:
        # 获取当前状态（此时应该是草稿写好了）
        snapshot = graph.get_state(config)
        if not snapshot.values:
            break
            
        current_report = snapshot.values.get("report_content")
        print("\n📝 --- 当前生成的日报 ---")
        print(current_report)
        
        # 人类介入
        user_input = input("\n👤 (输入 'ok' 发送，或输入修改意见): ")
        
        # 更新状态，把人的意见放进去
        graph.update_state(config, {"user_feedback": user_input})
        
        # 决定下一步：如果 ok 就继续跑(send)，如果不 ok 就回滚重跑(draft)
        # 这里的 resume 逻辑通过 stream(None) 继续
        # 但因为我们用了 Conditional Edge，只需让图继续运行即可
        
        # 我们给它一个 None 输入，让它继续从断点往下走
        # 路由函数 check_human_input 会读取刚才 update_state 进去的 feedback
        list(graph.stream(None, config))
        
        # 检查是否结束
        snapshot = graph.get_state(config)
        if not snapshot.next: # 如果没有后续步骤了，说明结束了
            print("🎉 任务结束！")
            break

if __name__ == "__main__":
    main()