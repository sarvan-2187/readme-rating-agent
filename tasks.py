from pydantic import BaseModel, Field
from crewai import Task
from textwrap import dedent

class EvaluationResult(BaseModel):
    repository_name: str = Field(description="Name of the repository evaluated (e.g. owner/repo)")
    overall_score: float = Field(description="Weighted overall score out of 5.0 (one decimal place)")
    project_overview_score: float = Field(description="Score for project overview (0.0 to 5.0)")
    clarity_of_purpose_score: float = Field(description="Score for clarity of purpose (0.0 to 5.0)")
    installation_guide_score: float = Field(description="Score for installation guide (0.0 to 5.0)")
    usage_documentation_score: float = Field(description="Score for usage documentation (0.0 to 5.0)")
    features_explanation_score: float = Field(description="Score for features explanation (0.0 to 5.0)")
    project_structure_score: float = Field(description="Score for project structure (0.0 to 5.0)")
    readability_score: float = Field(description="Score for readability (0.0 to 5.0)")
    accessibility_score: float = Field(description="Score for accessibility (0.0 to 5.0)")
    markdown_quality_score: float = Field(description="Score for markdown quality (0.0 to 5.0)")
    developer_experience_score: float = Field(description="Score for developer experience (0.0 to 5.0)")
    visual_presentation_score: float = Field(description="Score for visual presentation (0.0 to 5.0)")
    contribution_guidelines_score: float = Field(description="Score for contribution guidelines (0.0 to 5.0)")
    license_score: float = Field(description="Score for license (0.0 to 5.0)")
    professionalism_score: float = Field(description="Score for professionalism (0.0 to 5.0)")
    overall_completeness_score: float = Field(description="Score for overall completeness (0.0 to 5.0)")
    strengths: list[str] = Field(description="List of top strengths of the README")
    weaknesses: list[str] = Field(description="List of weaknesses of the README")
    missing_sections: list[str] = Field(description="List of missing sections that should be added")
    top_improvements: list[str] = Field(description="List of top improvements recommended")
    final_verdict: str = Field(description="A short paragraph summarizing the final verdict")

def create_evaluation_task(agent, github_url: str) -> Task:
    """Creates the task for evaluating the README."""
    
    description = dedent(f"""
        1. Use the 'Read GitHub Repository README' tool to fetch the README content for the repository: {github_url}.
        2. Analyze the fetched documentation rigorously based on the following criteria:
           - Project overview
           - Clarity of purpose
           - Installation guide
           - Usage documentation
           - Features explanation
           - Project structure
           - Readability
           - Accessibility
           - Markdown quality
           - Developer experience
           - Visual presentation
           - Contribution guidelines
           - License
           - Professionalism
           - Overall completeness
        3. Score each category on a scale of 0.0 to 5.0. Be critical and objective.
        4. Calculate a weighted overall score out of 5.0. 
        5. Identify strengths, weaknesses, missing sections, and top improvements.
        6. Produce a final verdict paragraph.
        
        Ensure your final output perfectly matches the requested JSON structure.
    """)
    
    expected_output = "A highly detailed evaluation report structured as the specified EvaluationResult JSON."
    
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        output_pydantic=EvaluationResult
    )
