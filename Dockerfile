FROM python:3.11-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager (faster and better dependency resolution)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy the repository content
COPY . /app

# Use uv to install dependencies with specific versions for CORS fix
RUN uv pip install --no-cache "langgraph-cli[inmem]>=0.1.73" "langgraph-api>=0.0.26" && \
    uv pip install --no-cache --editable .

# Default environment variables for Ollama
# In docker-compose, this should be set to http://ollama:11434
ENV OLLAMA_BASE_URL="http://ollama:11434"

# Expose the port that LangGraph dev server uses
EXPOSE 2024

# Launch with fixed host and port to avoid CORS issues
CMD ["uvx", \
     "--refresh", \
     "--from", "langgraph-cli[inmem]>=0.1.73", \
     "--with-editable", ".", \
     "--python", "3.11", \
     "langgraph", \
     "dev", \
     "--host", "localhost", \
     "--port", "2024"]