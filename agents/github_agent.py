import os
import logfire
from fastmcp.client.transports import StdioTransport
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.mcp import MCPToolset
from pydantic_ai import Agent

MCP_URL = os.environ.get("GITHUB_MCP_URL")
GITHUB_PAT = os.environ.get("GITHUB_PAT")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL")

logfire.configure()  
logfire.instrument_pydantic_ai()

ollama_model = OllamaModel(OLLAMA_MODEL)

transport = StdioTransport(
    command="docker",
    args=[
        "run", "--rm", "-i",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server",
        "stdio",
        "--toolsets", "repos,git,context",
        "--read-only",
    ],
    env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_PAT},
)

github_toolset = MCPToolset(transport)

github_agent = Agent (
    model = ollama_model,
    toolsets=[github_toolset],
    system_prompt=(
        "You are a code analysis specialist. "
        "Your task: find relevant files, indentify important symbols and understand the codebase. "
        "Use the available GitHub tools to read repository files and answer questions."
    )
)

def ask_sync(question:str) -> str:
    print("Agent called: github_agent")
    result = github_agent.run_sync(question)
    return result.output