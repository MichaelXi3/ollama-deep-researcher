# Ollama Deep Researcher

Ollama Deep Researcher is a fully local web research assistant that uses any LLM hosted by [Ollama](https://ollama.com/search). Give it a topic and it will generate a web search query, gather web search results (via [Tavily](https://www.tavily.com/) by default), summarize the results of web search, reflect on the summary to examine knowledge gaps, generate a new search query to address the gaps, search, and improve the summary for a user-defined number of cycles. It will provide the user a final markdown summary with all sources used.

![research-rabbit](https://github.com/user-attachments/assets/4308ee9c-abf3-4abb-9d1e-83e7c2c3f187)

Short summary:
<video src="https://github.com/user-attachments/assets/02084902-f067-4658-9683-ff312cab7944" controls></video>

## 📺 Video Tutorials

See it in action or build it yourself? Check out these helpful video tutorials:
- [Overview of Ollama Deep Researcher with R1](https://www.youtube.com/watch?v=sGUjmyfof4Q) - Load and test [DeepSeek R1](https://api-docs.deepseek.com/news/news250120) [distilled models](https://ollama.com/library/deepseek-r1).
- [Building Ollama Deep Researcher from Scratch](https://www.youtube.com/watch?v=XGuTzHoqlj8) - Overview of how this is built.

## 🚀 Quickstart

### Mac

1. Download the Ollama app for Mac [here](https://ollama.com/download).

2. Pull a local LLM from [Ollama](https://ollama.com/search). As an [example](https://ollama.com/library/deepseek-r1:8b):
```bash
ollama pull deepseek-r1:8b
```

3. Clone the repository:
```bash
git clone https://github.com/langchain-ai/ollama-deep-researcher.git
cd ollama-deep-researcher
```

4. Select a web search tool:

By default, it will use [DuckDuckGo](https://duckduckgo.com/) for web search, which does not require an API key. But you can also use [Tavily](https://tavily.com/) or [Perplexity](https://www.perplexity.ai/hub/blog/introducing-the-sonar-pro-api) by adding their API keys to the environment file:
```bash
cp .env.example .env
```
 
5. (Recommended) Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

6. Launch the assistant with the LangGraph server:

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
# uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev --host localhost --port 2024
```

### Windows

1. Download the Ollama app for Windows [here](https://ollama.com/download).

2. Pull a local LLM from [Ollama](https://ollama.com/search). As an [example](https://ollama.com/library/deepseek-r1:8b):
```powershell
ollama pull deepseek-r1:8b
```

3. Clone the repository:
```bash
git clone https://github.com/langchain-ai/ollama-deep-researcher.git
cd ollama-deep-researcher
```
 
4. Select a web search tool, as above.

5. (Recommended) Create a virtual environment: Install `Python 3.11` (and add to PATH during installation). Restart your terminal to ensure Python is available, then create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

6. Launch the assistant with the LangGraph server:

```powershell
# Install dependencies
pip install -e .
pip install langgraph-cli[inmem]

# Start the LangGraph server
langgraph dev
```

### Using the LangGraph Studio UI

When you launch LangGraph server, you should see the following output and Studio will open in your browser:
> Ready!
>
> API: http://127.0.0.1:2024
>
> Docs: http://127.0.0.1:2024/docs
>
> LangGraph Studio Web UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

Open `LangGraph Studio Web UI` via the URL in the output above.

In the `configuration` tab:
* Pick your web search tool (DuckDuckGo, Tavily, or Perplexity) (it will by default be `DuckDuckGo`) 
* Set the name of your local LLM to use with Ollama (it will by default be `llama3.2`) 
* You can set the depth of the research iterations (it will by default be `3`)

<img width="1621" alt="Screenshot 2025-01-24 at 10 08 31 PM" src="https://github.com/user-attachments/assets/7cfd0e04-28fd-4cfa-aee5-9a556d74ab21" />

Give the assistant a topic for research, and you can visualize its process!

<img width="1621" alt="Screenshot 2025-01-24 at 10 08 22 PM" src="https://github.com/user-attachments/assets/4de6bd89-4f3b-424c-a9cb-70ebd3d45c5f" />

### Model Compatibility Note

When selecting a local LLM, note that this application relies on the model's ability to produce structured JSON output. Some models may have difficulty with this requirement:

- **Working well**: 
  - [Llama2 3.2](https://ollama.com/library/llama3.2)
  - [DeepSeek R1 (8B)](https://ollama.com/library/deepseek-r1:8b)
  
- **Known issues**:
  - [DeepSeek R1 (7B)](https://ollama.com/library/deepseek-llm:7b) - Currently has difficulty producing required JSON output
  
If you [encounter JSON-related errors](https://github.com/langchain-ai/ollama-deep-researcher/issues/18) (e.g., `KeyError: 'query'`), try switching to one of the confirmed working models.

### Browser Compatibility Note

When accessing the LangGraph Studio UI:
- Firefox is recommended for the best experience
- Safari users may encounter security warnings due to mixed content (HTTPS/HTTP)
- If you encounter issues, try:
  1. Using Firefox or another browser
  2. Disabling ad-blocking extensions
  3. Checking browser console for specific error messages

## How it works

Ollama Deep Researcher is inspired by [IterDRAG](https://arxiv.org/html/2410.04343v1#:~:text=To%20tackle%20this%20issue%2C%20we,used%20to%20generate%20intermediate%20answers.). This approach will decompose a query into sub-queries, retrieve documents for each one, answer the sub-query, and then build on the answer by retrieving docs for the second sub-query. Here, we do similar:
- Given a user-provided topic, use a local LLM (via [Ollama](https://ollama.com/search)) to generate a web search query
- Uses a search engine (configured for [DuckDuckGo](https://duckduckgo.com/), [Tavily](https://www.tavily.com/), or [Perplexity](https://www.perplexity.ai/hub/blog/introducing-the-sonar-pro-api)) to find relevant sources
- Uses LLM to summarize the findings from web search related to the user-provided research topic
- Then, it uses the LLM to reflect on the summary, identifying knowledge gaps
- It generates a new search query to address the knowledge gaps
- The process repeats, with the summary being iteratively updated with new information from web search
- It will repeat down the research rabbit hole
- Runs for a configurable number of iterations (see `configuration` tab)

## Outputs

The output of the graph is a markdown file containing the research summary, with citations to the sources used.

All sources gathered during research are saved to the graph state.

You can visualize them in the graph state, which is visible in LangGraph Studio:

![Screenshot 2024-12-05 at 4 08 59 PM](https://github.com/user-attachments/assets/e8ac1c0b-9acb-4a75-8c15-4e677e92f6cb)

The final summary is saved to the graph state as well:

![Screenshot 2024-12-05 at 4 10 11 PM](https://github.com/user-attachments/assets/f6d997d5-9de5-495f-8556-7d3891f6bc96)

## Deployment Options

There are [various ways](https://langchain-ai.github.io/langgraph/concepts/#deployment-options) to deploy this graph.

See [Module 6](https://github.com/langchain-ai/langchain-academy/tree/main/module-6) of LangChain Academy for a detailed walkthrough of deployment options with LangGraph.

## TypeScript Implementation

A TypeScript port of this project (without Perplexity search) is available at:
https://github.com/PacoVK/ollama-deep-researcher-ts

## Running as a Docker container

The included `Dockerfile` only runs LangChain Studio with ollama-deep-researcher as a service, but does not include Ollama as a dependant service. You must run Ollama separately and configure the `OLLAMA_BASE_URL` environment variable.

Clone the repo and build an image:
```
$ docker build -t ollama-deep-researcher .
```

Run the container:
```
$ docker run --rm -it -p 2024:2024 \
  -e TAVILY_API_KEY="tvly-***YOUR_KEY_HERE***" \
  -e OLLAMA_BASE_URL="http://host.docker.internal:11434/" \
  ollama-deep-researcher
```

NOTE: You will see log message:
```
2025-02-10T13:45:04.784915Z [info     ] 🎨 Opening Studio in your browser... [browser_opener] api_variant=local_dev message=🎨 Opening Studio in your browser...
URL: https://smith.langchain.com/studio/?baseUrl=http://0.0.0.0:2024
```
...but the browser will not launch from the container.

Instead, visit this link with the correct baseUrl IP address: [`https://smith.langchain.com/studio/thread?baseUrl=http://127.0.0.1:2024`](https://smith.langchain.com/studio/thread?baseUrl=http://127.0.0.1:2024)

## Project Structure

The codebase has been refactored for better organization and to eliminate code duplication:

```
src/assistant/
├── common/                    # Shared utilities and components
│   ├── state.py              # Unified state classes
│   ├── search_tools.py       # Search tool functions
│   ├── source_utils.py       # Source formatting utilities
│   ├── prompts.py            # Shared prompt templates
│   └── llm.py                # LLM configuration
├── deep_research/            # Deep research graph
│   ├── interface.py          # Public interface
│   ├── graph.py              # Graph implementation
│   └── models.py             # Research models
├── newsletter/               # Newsletter graph
│   └── graph.py              # Graph implementation
├── configuration.py          # Configuration settings
├── base_research_graph.py    # Base research functionality
├── research_newsletter_runner.py # Combined runner
└── utils.py                  # Other utility functions
```

This structure eliminates duplicate code while maintaining clear separation of concerns:

- The `common` directory contains shared components used by multiple modules
- State definitions are consolidated into a common module with inheritance
- Search functionality and prompt templates are unified and reusable
- Each module (deep_research, newsletter) focuses solely on its own unique implementation

# Basic usage without deep research
runner = ResearchNewsletterRunner()
result = await runner.run()

# Enable deep research
result = await runner.run(use_deep_research=True)

# Customize categories and date
result = await runner.run(
    categories=["AI & ML", "Blockchain", "Cloud Computing"],
    use_deep_research=True,
    date="2024-02-23"
)