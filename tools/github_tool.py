import httpx
from datetime import datetime, timedelta


def _normalize_repos(repos):
    if isinstance(repos, str):
        return [r.strip() for r in repos.split(",") if r.strip()]
    if isinstance(repos, (list, tuple)):
        return [str(r).strip() for r in repos if str(r).strip()]
    return []


def _list_branches(username: str, repo: str, headers: dict):
    url = f"https://api.github.com/repos/{username}/{repo}/branches"
    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    return [b["name"] for b in response.json()]


def _filter_branches(branches, patterns):
    if not patterns:
        return branches
    lowered = [p.lower() for p in patterns if p]
    return [b for b in branches if any(p in b.lower() for p in lowered)]


def _date_range_for_commits(date_str: str):
    if not date_str:
        since = datetime.now() - timedelta(days=1)
        return since.isoformat(), None
    target = datetime.strptime(date_str, "%Y-%m-%d")
    since = target.replace(hour=0, minute=0, second=0, microsecond=0)
    until = since + timedelta(days=1)
    return since.isoformat(), until.isoformat()


def fetch_github_commits(username: str, repos, sha: str, token: str, branch_filter=None, date_str: str = ""):
    """抓取指定用户在指定仓库过去24小时的提交记录"""
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    since_date, until_date = _date_range_for_commits(date_str)
    repo_list = _normalize_repos(repos)
    if not repo_list:
        return "❌ 错误：未配置 GITHUB_REPO。"
    filter_patterns = _normalize_repos(branch_filter)

    logs = []
    seen_shas = set()

    for repo in repo_list:
        try:
            if sha:
                branches = [sha]
            else:
                branches = _list_branches(username, repo, headers)
                branches = _filter_branches(branches, filter_patterns)

            for branch in branches:
                url = f"https://api.github.com/repos/{username}/{repo}/commits"
                params = {"since": since_date, "author": username, "sha": branch}
                if until_date:
                    params["until"] = until_date
                response = httpx.get(url, headers=headers, params=params)
                response.raise_for_status()
                commits = response.json()

                for c in commits:
                    commit_sha = c.get("sha")
                    if commit_sha in seen_shas:
                        continue
                    seen_shas.add(commit_sha)
                    msg = c["commit"]["message"]
                    date = c["commit"]["author"]["date"]
                    logs.append(f"[{date}] ({repo}@{branch}) {msg}")
        except Exception as e:
            logs.append(f"[{repo}] 获取失败: {str(e)}")

    if not logs:
        return "今天没有检测到提交记录。"

    return "\n".join(logs)
