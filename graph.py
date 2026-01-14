from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver # 内存记忆，用于暂停
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


# 导入工具 (实际开发中引入上面的 github_tool)
# from tools.github_tool import fetch_github_commits
import os
from dotenv import load_dotenv
from tools.github_tool import fetch_github_commits # 记得导入工具

# 加载 .env 文件
load_dotenv()
# --- 1. 定义状态 ---
class DailyReportState(TypedDict):
    github_username: str
    repo_name: str
    raw_logs: str
    report_content: str
    user_feedback: str # 用户的修改意见

# --- 2. 节点逻辑 ---

def fetch_logs(state: DailyReportState):
    print("🤖 正在去 GitHub 搬砖...")
    
    # 从状态中获取用户名和仓库名
    username = state['github_username']
    repo = state['repo_name']
    
    # ✅ 从环境变量获取 Token (关键点！)
    token = os.getenv("GITHUB_TOKEN")
    sha = os.getenv("GITHUB_SHA")
    if not token:
        return {"raw_logs": "❌ 错误：未找到 GITHUB_TOKEN，请检查 .env 文件"}

    # 调用工具
    logs = fetch_github_commits(username, repo, sha, token)
    
    return {"raw_logs": logs}

def draft_report(state: DailyReportState):
    """步骤2：AI 写日报"""
    print("🤖 正在绞尽脑汁润色日报...")
    
    # 🌟 显式读取配置，这样更清楚，也更不容易出错
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE")
    
    # 如果是 DeepSeek，模型名字通常是 "deepseek-chat" 或 "deepseek-coder"
    # 如果是 OpenAI，就是 "gpt-4o"
    # 我们可以把模型名字也放到 .env 里，这里先写死 deepseek-chat 举例
    model_name = "deepseek-chat" 

    llm = ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=api_key,       # 👈 显式传参
        base_url=base_url      # 👈 显式传参 (关键！否则它会去连 OpenAI 官网)
    )
    
    prompt = f"""
    你是一个职场老手，请把下面的代码提交记录润色成一份专业的日报。
    风格要求：简洁、专业、体现价值。
    
    提交记录：
    {state['raw_logs']}
    
    {f'注意用户刚才的修改意见：{state["user_feedback"]}' if state.get("user_feedback") else ""}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"report_content": response.content}

def human_review(state: DailyReportState):
    """步骤3：展示给用户看 (这一步不改状态，只打印)"""
    print("\n" + "="*20 + " 日报草稿 " + "="*20)
    print(state['report_content'])
    print("="*50)
    print("👉 请检查：输入 'ok' 发送，或者直接输入修改意见。")
    # 这里不需要返回任何东西，因为下一条边是中断
    return

def send_message(state: DailyReportState):
    """步骤4：发送最终版"""
    print("🚀 正在通过飞书 Webhook 发送给领导...")
    # 这里调用飞书 API
    print(f"✅ 发送成功！内容：\n{state['report_content']}")
    return

# --- 3. 边的逻辑 ---

def check_human_input(state: DailyReportState):
    """路由逻辑：根据用户反馈决定下一步"""
    feedback = state.get("user_feedback", "").lower()
    if feedback == "ok":
        return "send"
    else:
        return "rewrite"

# --- 4. 构建图 ---
builder = StateGraph(DailyReportState)

builder.add_node("fetch", fetch_logs)
builder.add_node("draft", draft_report)
builder.add_node("review_node", human_review) # 这个节点只是为了占位展示
builder.add_node("send", send_message)

builder.set_entry_point("fetch")
builder.add_edge("fetch", "draft")
builder.add_edge("draft", "review_node")

# 关键：在这里加入条件路由
builder.add_conditional_edges(
    "review_node",
    check_human_input,
    {
        "send": "send",
        "rewrite": "draft"
    }
)
builder.add_edge("send", END)

# 启用记忆，这样才能在“review_node”后暂停并恢复
memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["review_node"])