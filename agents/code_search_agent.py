from pydantic import BaseModel
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai import Agent

class CodeSearchResult(BaseModel):
    explanation: str
    path: str
    snippet: str | None = None
    
def build_code_search_agent(model: OpenAIChatModel, toolset: MCPToolset) -> Agent:
    return Agent(
        model = model,
        toolsets=[toolset],
        output_type=list[CodeSearchResult],
        system_prompt="""
        You are a code search agent.

        Your job:
        1. Understand the user question about the codebase.
        2. Use search_code to find relevant files.
        3. Use file reading tools to inspect important files.
        4. Return only the most relevant code locations.

        Rules:
        - Always start with search_code.
        - Read files only if necessary.
        - Do NOT guess.
        - Prefer 3-5 files max.
        - Focus on architecture-relevant code (controllers, services, APIs).
        """
    )

def run_code_search_agent(question: str, repo_url: str, code_search_agent: Agent) -> list[CodeSearchResult]:
    user_prompt = question + "repo_url: " + repo_url
    
    print("Agent called: code_search_agent")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = code_search_agent.run_sync(user_prompt)
            return result.output
        except Exception as e:
           print(e)
           
    return []
