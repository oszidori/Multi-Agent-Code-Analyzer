# Multi-Agent Code Analyzer

A Python project that coordinates multiple AI agents to inspect GitHub codebases, search for code details, and analyze architecture or technology decisions all through a conversational CLI.

## Overview

The system routes your questions to specialized sub-agents via an orchestrator:

- **GitHub agent**: fetches repository metadata and file contents via a GitHub MCP server
- **Code search agent**: searches for specific symbols, patterns, or implementations
- **Architecture agent**: identifies design patterns and explains architectural decisions
- **Orchestrator**: manages conversation state and delegates tasks to the right agent

## Features

- Conversational CLI: ask questions about any GitHub repository in natural language
- Multi-turn context: the orchestrator maintains message history across turns
- Architecture pattern detection and technology explanation backed by a local knowledge base (`knowledge/`)
- Observability via Logfire (traces all agent calls)

## Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A [GitHub Personal Access Token](https://github.com/settings/tokens) with `repo` read scope
- Docker Desktop
- A GitHub MCP server running locally at the URL set in `GITHUB_MCP_URL` (default: `http://localhost:8080/mcp`)

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```powershell
Copy-Item .env.example .env
```

Required variables:

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `GPT_MODEL` | Model name, e.g. `gpt-4o-mini` |
| `GITHUB_PAT` | GitHub Personal Access Token |
| `GITHUB_MCP_URL` | URL of your running GitHub MCP server |
| `COMMON_TECH_PATH` | Absolute path to `knowledge/common_technologies.json` |
| `DESIGN_PATTERNS_PATH` | Absolute path to `knowledge/common_design_patterns.json` |

Load the variables into your shell session:

```powershell
.\load_env.ps1
```

## Running the Application

Make sure the GitHub MCP server is running, then start the chat:

```powershell
python app.py
```

**Usage flow:**

1. Find a repository you want to analyze (e.g., `Find acmeair repository owned by acmeair`).
2. Wait for the agent to fetch context.
3. Ask any question about the codebase: architecture, specific code, technologies used, etc.
4. Type `exit` to quit.

## Project Structure

```
.
├── app.py                    # Entry point — starts the conversational CLI
├── multi_agent_system.py     # Core coordination and toolset wiring
├── agents/
│   ├── orchestrator_agent.py # Routes tasks and maintains conversation state
│   ├── github_agent.py       # GitHub repository access via MCP
│   ├── code_search_agent.py  # Code-level search via MCP
│   └── architecture_agent.py # Architecture and pattern analysis
├── tools/
│   ├── github_mcp.py         # MCP transport wrapper for GitHub
│   ├── architecture_tool.py  # Pattern detection logic
│   └── technology_tool.py    # Technology explanation logic
├── knowledge/
│   ├── common_technologies.json    # Technology knowledge base
│   └── common_design_patterns.json # Design pattern knowledge base
├── .env.example              # Environment variable template
├── load_env.ps1              # Loads .env into the current shell session
└── requirements.txt
```

## Dependencies

| Package | Purpose |
|---|---|
| `pydantic-ai` | Agent framework and MCP toolset integration |
| `pydantic` | Data models and validation |
| `openai` | OpenAI model client (used by pydantic-ai) |
| `fastmcp` | MCP client transport layer |
| `logfire` | Observability and tracing |
