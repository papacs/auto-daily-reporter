# AGENTS.md

Project: Auto Daily Reporter (Python 3.10+, LangGraph-based CLI tool that pulls GitHub commits, drafts a daily report with LLM, and supports human-in-the-loop edits).

## Quick context
- Primary entrypoint: `main.py`
- Orchestration/graph logic: `graph.py`
- MCP server/tooling: `mcp_server.py`, `tools/`
- Dependencies: `requirements.txt`

## Common tasks
- Install deps: `pip install -r requirements.txt`
- Run CLI: `python main.py`

## Environment/config
- Copy `.env.example` to `.env` and fill:
  - `GITHUB_TOKEN`, `GITHUB_USER`, `GITHUB_REPO`
  - `OPENAI_API_KEY`, `OPENAI_API_BASE` (DeepSeek/OpenAI compatible)

## Project behavior summary
- Fetches same-day GitHub commits from a branch (e.g., `dev`)
- LLM rewrites commits into a structured daily report
- Human-in-the-loop confirmation: user can approve or request edits

## Notes for changes
- Keep output readable and professional; avoid fabricating work items.
- Preserve the CLI flow: fetch -> draft -> review -> send.
