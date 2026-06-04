from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai import FunctionToolset, Agent
from tools.architecture_tool import ArchitectureFacts

def build_architecture_agent(model: OpenAIChatModel, toolset: FunctionToolset) -> Agent:
    return Agent(
        model = model,
        toolsets=[toolset],
        system_prompt = """
        You are a code expert architect agent.

        You will receive a user question and the architecture facts of a codebase.

        Tool usage rules — follow these strictly:
        - Call explain_technology when the user asks:
        - What a technology is ("what is MongoDB?", "explain Redis", "what does Kafka do?")
        - A technology's purpose, role, or how it works even if it is not in the codebase facts
        - About the tech stack or specific technologies used in the codebase
        - Call detect_patterns when the user explicitly asks about design patterns, architectural
        patterns, or how the code is structured in terms of patterns.
        - Do NOT guess. Answer only from the facts and tool results.
        """
    )

def run_architecture_agent(question: str, facts: ArchitectureFacts, architecture_agent: Agent) -> str:
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
    errors = []
    
    for attempt in range(max_retries):
        try:
            result = architecture_agent.run_sync(user_prompt)
            return result.output
        except Exception as e:
           errors.append(e)
           
    return f"Architecture agent failed after {max_retries} attempts. Errors: {errors}"