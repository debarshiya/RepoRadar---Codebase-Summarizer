## How to Run RepoRadar
RepoRadar is designed to be easy to set up and run locally for any Python repository.
Follow these simple steps to get started:
1. Clone the Repo
```bash
git clone https://github.com/<your-username>/RepoRadar.git
cd RepoRadar
```bash

2. Set Up the Environment
Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate    # on macOS/Linux
venv\Scripts\activate       # on Windows
```bash

3. Install Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```bash

4. Add Your API Key
RepoRadar uses an LLM for code summarization (OpenAI or OpenRouter).
Create a .env file in the project root and add your API key:
```bash
# Example for OpenAI or OpenRouter
OPENROUTER_API_KEY=your_api_key_here
```bash

5. Run the App
Launch the Streamlit interface:
```bash
streamlit run src/app.py
```bash

6. Explore Any Repository
- Paste a GitHub repo link in the input box to clone it automatically to analyze an existing repo.
- Click Analyze Repository to parse files and functions.
- Use Summarize to generate AI-based summaries and docstrings.
- Click Build Graph to visualize dependencies across the project.

## Inspiration
As developers, we’ve all faced the frustration of diving into a new or legacy repository without documentation — jumping between files, tracing imports, and piecing together logic line by line.  
We wanted to make this process effortless. RepoRadar was inspired by that idea — a “radar” for repositories that scans, understands, and explains code intelligently.

## What it does
RepoRadar automatically analyzes any Python codebase to:  
- Parse all files, functions, and classes using static analysis  
- Generate **AI-based summaries** and **docstring suggestions**  
- Build an **interactive dependency graph** showing how code components connect  
- Let users explore summaries and visualizations directly through a **Streamlit interface**  

In short — it helps you *understand a repository in minutes instead of hours.*

## How we built it
We built RepoRadar by combining **AST parsing, LLM summarization, and interactive visualization**:  
- 🧩 Parsed Python files using `ast` and `asttokens` to extract structure and function relationships  
- 🤖 Used OpenRouter’s LLM API (like *Microsoft Phi-3.5 Mini* and *GPT-4o Mini*) to summarize each code chunk  
- 📊 Visualized dependencies with **PyVis** and **NetworkX**  
- 🖥️ Built a stylish minimalistic and responsive UI with **Streamlit**  
- 💾 Added caching for summaries to improve performance  

## Challenges we ran into
- Handling **complex nested imports** and circular dependencies.  
- Fixing the **PyVis template rendering error** (`template.render`) when generating graphs.  
- Avoiding **cached summaries** from older runs when switching between files.  
- Managing **branch merges and dependency updates** across development environments.  

Each of these pushed us to refine the design and error handling to make RepoRadar functional and scalable.

## Accomplishments that we're proud of
- Fully integrated OpenRouter’s LLMs for automated summarization.  
- Solved caching and file-specific summarization issues.  
- Fixed PyVis rendering and dependency graph export.  
- Delivered a clean, minimal, and intuitive UI experience.  
- Built a project that genuinely helps developers *save time and think smarter.*

## What we learned
- Designing **prompt templates** for precise LLM code summarization.  
- Using **AST-based parsing** to analyze and extract Python code structures.  
- Debugging Streamlit state management for smoother interactivity.  
- Managing collaborative workflows with Git branching and merges.

## What's next for RepoRadar
- Extend support beyond Python — to JavaScript, Java, and C++.  
- Automate git checkout to compare two branches of the same repository and evaluate the differences 
- Integrate analytics to measure repository complexity and maintainability.
