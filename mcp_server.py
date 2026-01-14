import os
from mcp.server.fastmcp import FastMCP
from tools.github_tool import fetch_github_commits
from dotenv import load_dotenv 

# ✅ 关键点 1：必须加载 .env 文件，否则 os.getenv 读不到
load_dotenv() 

mcp = FastMCP("Auto-Daily-Reporter-MCP")

@mcp.tool()
def get_daily_commits(username: str, repo: str) -> str:
    """获取指定 GitHub 仓库今天的提交记录"""
    
    # 从环境变量读取 Token
    token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        return "❌ 错误：未在 .env 中找到 GITHUB_TOKEN"
    
    # ✅ 关键点 2：调用时必须把 token 传进去！
    # ❌ 错误写法：return fetch_github_commits(username, repo)  <-- 报错就是因为写成了这样
    # ✅ 正确写法：
    return fetch_github_commits(username, repo, token)

if __name__ == "__main__":
    mcp.run()

    # npx @modelcontextprotocol/inspector python mcp_server.py

    # http://localhost:5173