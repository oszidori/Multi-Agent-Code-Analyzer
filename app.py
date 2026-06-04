import logfire
import os

from pydantic_ai.models.openai import OpenAIChatModel
from agents.orchestrator_agent import RepositoryContextHolder, build_orchestrator_agent
from multi_agent_system import build_orch_toolset

logfire.configure()  
logfire.instrument_pydantic_ai()

GPT_MODEL = os.environ.get("GPT_MODEL")
model = OpenAIChatModel(GPT_MODEL)

orchestration_toolset = build_orch_toolset()
orchestrator_agent = build_orchestrator_agent(model, orchestration_toolset)

def chat():
    print("Code Analyzer Multi Agent System — type 'exit' to quit\n")
    print("First step: give the repository name and owner you want to analyze.")
    print("Second step: wait the agent response and ask about the code base.")
    
    message_history = []
    holder = RepositoryContextHolder()
    
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        try:
            result = orchestrator_agent.run_sync(
                user_prompt = user_input, 
                deps = holder, 
                message_history = message_history
            )
            message_history = result.all_messages()
            print(f"\nAgent: {result.output}\n")
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    chat()