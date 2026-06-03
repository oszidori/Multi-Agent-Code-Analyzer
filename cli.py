import os
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai import FunctionToolset
import logfire
import typer
from tools.github_mcp import build_github_toolset
from tools.technology_tool import explain_technology
from tools.architecture_tool import detect_patterns, ArchitectureFacts
from agents.github_agent import build_github_agent, discover_repository
from agents.code_search_agent import build_code_search_agent, search_code
from agents.architecture_agent import build_architecture_agent, analyze_architecture
logfire.configure()  
logfire.instrument_pydantic_ai()

GPT_MODEL = os.environ.get("GPT_MODEL")
model = OpenAIChatModel(GPT_MODEL)

github_toolset = build_github_toolset()
github_agent = build_github_agent(github_toolset, model)
code_search_agent = build_code_search_agent(github_toolset, model)

arch_toolset = FunctionToolset(tools=[explain_technology, detect_patterns])
architecture_agent = build_architecture_agent(model, arch_toolset)

app = typer.Typer()

@app.command()
def ask(question: str):
    """Ask a question about a GitHub repository's code."""
    print(f"The given repo name: {question}")
    answer = discover_repository(question, github_agent)
    print(answer) 
    new_question = input("Ask about something in the code: ")
    print(new_question)
    code_snippets = search_code(new_question, answer.repo_url, code_search_agent)
    for c in code_snippets:
        print(c)
    new_tech_question = input("Ask about something with the technologies: ") 
    print(new_tech_question)
    result = analyze_architecture(new_tech_question, answer.facts, architecture_agent)
    print(result)
    new_pattern_question = input("Ask about the architecture design pattern: ")
    new_result = analyze_architecture(new_pattern_question, answer.facts, architecture_agent)
    print(new_result)
        
        
test_facts = ArchitectureFacts(
    technologies=[
        "spring boot",
        "docker"
    ],
    modules=[
        "controller",
        "service",
        "repository"
    ],
    protocols=[],
    annotations=[
        "@RestController"
    ],
    keywords=[]
)

@app.command()
def check(name: str = "", is_technology: bool = False):
    """Test knowledge tools."""
    if is_technology:
        answer = explain_technology(name)
        print(answer)
    else:
        answer = detect_patterns(test_facts)
        for pattern in answer.patterns:
            print(f"{pattern.name}: {pattern.confidence}\n {pattern.breakdown}")

if __name__ == "__main__":
    app()
