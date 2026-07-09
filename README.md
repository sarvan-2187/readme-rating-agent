# GitHub README Rating Agent

A production-ready AI agent that evaluates the quality of a GitHub repository's README and assigns a rating out of **5.0**. It is built with Python, CrewAI, LangChain, Groq API (Llama 3 70B), and Rich for a beautiful CLI experience.

## Features

- **Automated Fetching**: Automatically fetches the README content using the GitHub API without needing to clone the repo.
- **AI Evaluation**: Employs an expert AI Agent specializing in Open Source Documentation, Developer Experience, and Markdown Best Practices.
- **Structured Scoring**: Evaluates the README against 15 distinct criteria and computes a weighted overall rating.
- **Actionable Feedback**: Identifies strengths, weaknesses, missing sections, and top improvements.
- **Beautiful CLI**: Uses Rich to render an elegant terminal interface with tables, panels, and progress spinners.

## Project Architecture

```text
readme-rating-agent/
│── agents.py          # Defines the Evaluator Agent
│── tasks.py           # Defines the Evaluation Task and Pydantic Schema
│── tools.py           # Custom CrewAI tool to fetch README via GitHub API
│── run.py             # Main CLI entrypoint, Rich UI rendering, and orchestration
│── requirements.txt   # Project dependencies
│── .env.example       # Example environment variables
│── README.md          # Project documentation
```

## Prerequisites

- Python 3.10+
- A valid [Groq API Key](https://console.groq.com/) for Llama 3 models.

## Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/sarvan-2187/readme-rating-agent.git
   cd readme-rating-agent
   ```

2. **Create a virtual environment (recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Groq API key:
   ```env
   GROQ_API_KEY=your_actual_api_key_here
   MODEL_NAME=llama3-70b-8192
   ```

## Running the Application

Execute the CLI by running:
```bash
python run.py
```

You will be prompted to enter a GitHub repository URL:
```text
Enter GitHub Repository URL: https://github.com/owner/repository
```

The agent will then begin processing the documentation. A spinner will indicate that the evaluation is in progress.

## Example Output

Once finished, the CLI will display:
- **Overall Rating**: The final score out of 5.0 and star rating.
- **Category Breakdown**: A table with individual scores for Readability, Accessibility, Developer Experience, etc.
- **Strengths & Weaknesses**: A side-by-side comparison of the documentation's pros and cons.
- **Actionable Feedback**: Suggested missing sections and top improvements.
- **Final Verdict**: A comprehensive summary written by the AI Agent.

## License

This project is licensed under the MIT License.
