from pydantic import BaseModel
from dataclasses import dataclass
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai import Agent, FunctionToolset

class ArchitectureFacts(BaseModel):
    technologies: list[str]
    modules: list[str]
    protocols: list[str]
    annotations: list[str]
    keywords: list[str]

class RepositoryContext(BaseModel):
    success: bool
    repo_url: str
    readme: str
    tree: str
    facts: ArchitectureFacts

@dataclass
class RepositoryContextHolder:
    context: RepositoryContext | None = None

def build_orchestrator_agent(model: OpenAIChatModel, toolset: FunctionToolset) -> Agent:
    return Agent(
        model=model,
        toolsets=[toolset],
        deps_type=RepositoryContextHolder,
        system_prompt= """
        You are a software repository analyst assistant. You talk directly with the user.

        You have access to three tools:
        - discover_repository: call this when the user provides a GitHub repository or asks about one.
        It fetches and stores the full repository context automatically.
        - search_code: call this for code-level questions (how something is implemented, where a class
        or function is defined, what a specific file contains). 
        - analyze_architecture: call this for architecture, technology stack, design pattern, or
        "what is X" technology questions. 

        Decision rules, follow these strictly:
        - If repository context is not yet loaded, call discover_repository first.
        - If repository context is already loaded from a previous turn, do NOT call discover_repository again.
        - For code-level questions (specific class, method, file, implementation detail), call search_code.
        - For architecture, technology, design pattern, or general technology questions, call analyze_architecture.
        - Never call a tool speculatively. Only call a tool when the user's question requires it.
        - Do NOT make up answers. All responses must be grounded in tool results.

        Communication style:
        - Be concise and direct.
        - Synthesize a clear, structured answer from tool results.
        - If a tool call fails, inform the user and ask them to verify the repository URL or question.
 """
    )