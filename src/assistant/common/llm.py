from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

def get_llm(config: RunnableConfig) -> ChatOpenAI:
    """Get a configured LLM instance."""
    model_name = config.get("model_name", "gpt-3.5-turbo")
    return ChatOpenAI(
        model=model_name,
        temperature=0,
    ) 