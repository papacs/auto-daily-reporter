import httpx
from datetime import datetime, timedelta


def fetch_github_commits(username: str, repo: str, sha: str, token: str):
    """抓取指定用户在指定仓库过去24小时的提交记录"""
    # 这里为了演示简单，我们直接请求 GitHub API 
    # 实际通用版可以扩展为抓取用户所有仓库的 Event
    url = f"https://api.github.com/repos/{username}/{repo}/commits"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    
    since_date = (datetime.now() - timedelta(days=1)).isoformat()
    params = {"since": since_date, "author": username,"sha": sha}
    
    try:
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        commits = response.json()
        
        if not commits:
            return "今天没有检测到提交记录。"
            
        logs = []
        for c in commits:
            msg = c['commit']['message']
            date = c['commit']['author']['date']
            logs.append(f"[{date}] {msg}")
        return "\n".join(logs)
    except Exception as e:
        return f"获取失败: {str(e)}"