import os
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic import BaseModel
from pydantic_ai import Agent
from tools.architecture_tool import ArchitectureFacts

class RepositoryContext(BaseModel):
    success: bool
    repo_url: str
    readme: str
    tree: str
    facts: ArchitectureFacts

def build_github_agent(github_toolset: MCPToolset, model: OpenAIChatModel):
    return Agent (
        model = model,
        toolsets=[github_toolset],
        output_type=RepositoryContext,
        system_prompt= """
            You are a code analysis specialist. 
            Your task: 
            1. Find the most relevant repository using the tools.
            2. Identify and understand repository architecture facts:
                - facts.technologies: frameworks, databases, messaging systems
                - facts.modules: top-level folders or logical layers
                - facts.protocols: communication protocols (http, amqp, grpc)
                - facts.annotations: code annotations visible in files (@RestController, etc.)
                - facts.keywords: DDD vocabulary (aggregate, domain, bounded context) 
            3. Use the available GitHub tools and answer questions.
        """
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
