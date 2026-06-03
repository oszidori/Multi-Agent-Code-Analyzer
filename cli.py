import typer

from agents.github_agent import ask_sync

app = typer.Typer()

@app.command()
def ask(question: str):
    """Ask a question about a GitHub repository's code."""
    print(f"Question: {question}")
    answer = ask_sync(question)
    print(answer)
    


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


if __name__ == "__main__":
    app()
