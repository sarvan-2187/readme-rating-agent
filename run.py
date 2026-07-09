import os
import sys

# Configure LiteLLM to drop unsupported parameters and fully disable CrewAI telemetry
os.environ["LITELLM_DROP_PARAMS"] = "True"
os.environ["CREWAI_TRACING_ENABLED"] = "False"
os.environ["OTEL_SDK_DISABLED"] = "true"   # Disables the OpenTelemetry SDK used by CrewAI tracing

# --- Workaround for CrewAI bug #5886 ---
# CrewAI injects `cache_breakpoint` into system messages for ALL providers,
# but Groq (and others) reject it. We monkey-patch the function to a no-op
# BEFORE any crewai internals are imported.
try:
    import crewai.llms.cache as _crewai_cache
    _crewai_cache.mark_cache_breakpoint = lambda msg: msg
except Exception:
    pass  # If the module path changes in future versions, fail silently

from dotenv import load_dotenv
from crewai import Crew, Process
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich.text import Text

from agents import create_evaluator_agent
from tasks import create_evaluation_task

# Load environment variables
load_dotenv()

console = Console()

def render_stars(score: float) -> str:
    """Helper to render a visual star rating."""
    full_stars = int(score)
    half_star = 1 if score - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    return "★" * full_stars + "½" * half_star + "☆" * empty_stars

def display_results(result):
    """Renders the EvaluationResult cleanly using Rich."""
    console.print("\n")
    
    # Title Panel
    title = Text(f"Evaluation Report: {result.repository_name}", style="bold cyan", justify="center")
    console.print(Panel(title, border_style="cyan"))
    
    # Overall Score Panel
    score_style = "bold green" if result.overall_score >= 4.0 else "bold yellow" if result.overall_score >= 3.0 else "bold red"
    stars = render_stars(result.overall_score)
    score_text = Text.assemble(
        ("Overall Rating: ", "bold white"),
        (f"{result.overall_score}/5.0 ", score_style),
        (f"[{stars}]", "yellow")
    )
    console.print(Panel(Align.center(score_text), border_style=score_style))
    
    # Categories Table
    table = Table(title="Category Breakdown", show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Category", style="dim", width=30)
    table.add_column("Score", justify="right", width=10)
    table.add_column("Rating", justify="left")

    categories = [
        ("Project Overview", result.project_overview_score),
        ("Clarity of Purpose", result.clarity_of_purpose_score),
        ("Installation Guide", result.installation_guide_score),
        ("Usage Documentation", result.usage_documentation_score),
        ("Features Explanation", result.features_explanation_score),
        ("Project Structure", result.project_structure_score),
        ("Readability", result.readability_score),
        ("Accessibility", result.accessibility_score),
        ("Markdown Quality", result.markdown_quality_score),
        ("Developer Experience", result.developer_experience_score),
        ("Visual Presentation", result.visual_presentation_score),
        ("Contribution Guidelines", result.contribution_guidelines_score),
        ("License", result.license_score),
        ("Professionalism", result.professionalism_score),
        ("Overall Completeness", result.overall_completeness_score),
    ]

    for cat, score in categories:
        cat_style = "green" if score >= 4.0 else "yellow" if score >= 3.0 else "red"
        table.add_row(cat, f"[{cat_style}]{score}[/{cat_style}]", f"[{cat_style}]{render_stars(score)}[/{cat_style}]")

    console.print(table)
    console.print("\n")

    # Strengths & Weaknesses Tables
    sw_table = Table(show_header=False, expand=True, box=None)
    sw_table.add_column("Strengths", style="green")
    sw_table.add_column("Weaknesses", style="red")
    
    # Determine max rows needed
    max_len = max(len(result.strengths), len(result.weaknesses))
    strengths_padded = result.strengths + [""] * (max_len - len(result.strengths))
    weaknesses_padded = result.weaknesses + [""] * (max_len - len(result.weaknesses))
    
    for s, w in zip(strengths_padded, weaknesses_padded):
        s_display = f"✔ {s}" if s else ""
        w_display = f"✘ {w}" if w else ""
        sw_table.add_row(s_display, w_display)
        
    console.print(Panel(sw_table, title="[bold]Strengths & Weaknesses", border_style="blue"))
    
    # Improvements & Missing Sections
    if result.missing_sections or result.top_improvements:
        imp_text = ""
        if result.missing_sections:
            imp_text += "[bold red]Missing Sections:[/bold red]\n"
            for m in result.missing_sections:
                imp_text += f"- {m}\n"
            imp_text += "\n"
            
        if result.top_improvements:
            imp_text += "[bold yellow]Top Improvements:[/bold yellow]\n"
            for i in result.top_improvements:
                imp_text += f"- {i}\n"
                
        console.print(Panel(imp_text.strip(), title="[bold]Actionable Feedback", border_style="yellow"))
    
    # Final Verdict
    console.print(Panel(result.final_verdict, title="[bold]Final Verdict", border_style="magenta"))

def main():
    console.clear()
    rprint("[bold blue]🚀 Welcome to the GitHub README Rating Agent CLI[/bold blue]\n")
    
    if not os.getenv("GROQ_API_KEY"):
        rprint("[bold red]Error:[/bold red] GROQ_API_KEY is not set. Please check your .env file.")
        sys.exit(1)
        
    github_url = Prompt.ask("Enter GitHub Repository URL")
    
    if not github_url or "github.com" not in github_url:
        rprint("[bold red]Invalid GitHub URL![/bold red] Please provide a valid repository URL.")
        sys.exit(1)

    try:
        agent = create_evaluator_agent()
        task = create_evaluation_task(agent, github_url)
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
            telemetry=False,
        )
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Agent is evaluating the README...", total=None)
            crew_output = crew.kickoff()
        
        # crew_output.pydantic should contain our EvaluationResult
        result = task.output.pydantic
        if not result:
             # Fallback if crewai didn't populate task.output.pydantic properly
             rprint("[bold yellow]Warning:[/bold yellow] Agent did not return structured output perfectly.")
             rprint(crew_output)
             sys.exit(1)
             
        display_results(result)
        
    except Exception as e:
        rprint(f"[bold red]An error occurred during evaluation:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
