import os
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic import BaseModel
from pydantic_ai import Agent

class RepositoryContext(BaseModel):
    success: bool
    repo_url: str
    readme: str
    tree: str
    tech_stack: list[str]

def build_github_agent(github_toolset: MCPToolset, model: OpenAIChatModel):
    return Agent (
        model = model,
        toolsets=[github_toolset],
        output_type=RepositoryContext,
        system_prompt=(
            "You are a code analysis specialist. "
            "Your task: find the most relevant repository and identify repository purpose, modules and tech stack. "
            "Use the available GitHub tools and answer questions."
        )
    )

def discover_repository(question:str, github_agent: Agent) -> RepositoryContext:
    print("Agent called: github_agent")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = github_agent.run_sync(question)
            return result.output
        except Exception as e:
           print(e)
            
    return RepositoryContext(success=False, repo_url="", readme="", tree="", tech_stack=[])
