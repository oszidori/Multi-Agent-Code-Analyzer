import os
from pydantic_ai.mcp import MCPToolset
from fastmcp.client.transports import StdioTransport

GITHUB_PAT = os.environ.get("GITHUB_PAT")

def build_github_toolset() -> MCPToolset:
    transport =  StdioTransport(
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
    return MCPToolset(transport)
