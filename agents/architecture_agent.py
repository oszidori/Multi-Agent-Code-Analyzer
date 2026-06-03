from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai import FunctionToolset, Agent
from tools.technology_tool import TechnologyInfo, explain_technology
from tools.architecture_tool import ArchitectureFacts, PatternDetectionResult, detect_patterns

def build_architecture_agent(model: OpenAIChatModel, toolset: FunctionToolset) -> Agent:
    return Agent(
        model = model,
        toolsets=[toolset],
        system_prompt = """
        You are a code expert architect agent.

        You will receive a user question and the architecture facts of a codebase.

        Tool usage rules — follow these strictly:
        - Call lookup_technology ONLY if the user asks about a specific technology, its role, or the tech stack.
        - Call find_design_patterns ONLY if the user explicitly asks about design patterns, architectural patterns, or how the code is structured in terms of patterns.
        - If the question is general (e.g. "what does this app do?"), answer from the facts alone without calling any tool.
        - Never call a tool just because it is available.
        - Do NOT guess. Answer only from the facts and tool results.
        """
    )

def analyze_architecture(question: str, facts: ArchitectureFacts, architecture_agent: Agent):
    user_prompt = f"""
        {question}
        The Architecture facts:
        technologies: {facts.technologies}
        modules: {facts.modules}
        protocols: {facts.protocols}
        annotations: {facts.annotations}
        keywords: {facts.keywords}
    """
    
    print("Agent called: architecture_agent")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = architecture_agent.run_sync(user_prompt)
            return result.output
        except Exception as e:
           print(e)
           
    return []