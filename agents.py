import os
from crewai import Agent
from crewai import LLM
from tools import fetch_readme_content


def get_llm() -> LLM:
    """Returns a configured CrewAI LLM instance for Groq."""
    api_key = os.getenv("GROQ_API_KEY")
    model_name = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please check your .env file.")

    # Use CrewAI's native LLM class with drop_params to suppress unsupported
    # provider-specific fields like `cache_breakpoint` that Groq rejects.
    return LLM(
        model=f"groq/{model_name}",
        api_key=api_key,
        temperature=0.2,
        drop_params=True,
    )


def create_evaluator_agent() -> Agent:
    """Creates the documentation evaluator agent."""

    system_prompt = (
        "You are an elite Technical Documentation Reviewer specializing in Open Source Documentation, "
        "Developer Experience, and Markdown Best Practices. "
        "Your role is to critically analyze GitHub README files and evaluate them based on industry standards. "
        "You look for clarity, completeness, proper structure, visual presentation, accessibility, and overall professionalism. "
        "You provide constructive, objective, and detailed assessments."
    )

    return Agent(
        role="Senior Technical Documentation Reviewer",
        goal="Evaluate GitHub repository README files and assign accurate, well-reasoned ratings.",
        backstory=system_prompt,
        verbose=True,
        allow_delegation=False,
        llm=get_llm(),
        tools=[fetch_readme_content],
    )
