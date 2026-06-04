from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai import FunctionToolset, Agent, RunContext
import os

from agents.github_agent import RepositoryContext, build_github_agent, run_github_agent
from agents.code_search_agent import CodeSearchResult, build_code_search_agent, run_code_search_agent
from agents.architecture_agent import build_architecture_agent, run_architecture_agent

from agents.orchestrator_agent import RepositoryContextHolder
from tools.github_mcp import build_github_toolset
from tools.technology_tool import explain_technology
from tools.architecture_tool import detect_patterns, ArchitectureFacts

GPT_MODEL = os.environ.get("GPT_MODEL")
model = OpenAIChatModel(GPT_MODEL)

github_agent = build_github_agent(model, build_github_toolset())
code_search_agent = build_code_search_agent(model, build_github_toolset())

arch_toolset = FunctionToolset(tools=[explain_technology, detect_patterns])
architecture_agent = build_architecture_agent(model, arch_toolset)

def discover_repository(ctx: RunContext[RepositoryContextHolder],question: str) -> str:
    """Fetch a GitHub repository's structure, technologies, and architecture facts."""
    ctx.deps.context = run_github_agent(question, github_agent)
    return f"Repository context loaded for: {ctx.deps.context.repo_url}"

def search_code(ctx: RunContext[RepositoryContextHolder], question: str) -> list[CodeSearchResult]:
    """Search for specific code details. Repository context must already be loaded."""
    return run_code_search_agent(question, ctx.deps.context.repo_url, code_search_agent)
    
def analyze_architecture(ctx: RunContext[RepositoryContextHolder], question: str) -> str:
    """Answer architecture, technology, or design pattern questions. Repository context must already be loaded."""
    return run_architecture_agent(question, ctx.deps.context.facts, architecture_agent)

def build_orch_toolset() -> FunctionToolset:
    return FunctionToolset(tools=[discover_repository, search_code, analyze_architecture])
