import os
from dataclasses import dataclass, fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from dataclasses import dataclass

from enum import Enum

class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"
    DUCKDUCKGO = "duckduckgo"

@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the research assistant."""
    max_web_research_loops: int = 3
    local_llm: str = "deepseek-r1:32b"
    search_api: SearchAPI = SearchAPI.DUCKDUCKGO  # Default to DUCDUCKGO
    fetch_full_page: bool = False  # Default to False
    ollama_base_url: str = "http://localhost:11434/"

    @classmethod
    def from_runnable_config(cls, config: Optional[RunnableConfig] = None) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig.
        
        Args:
            config: Optional configuration dictionary that may contain 'configurable' settings
            
        Returns:
            Configuration: A new instance with values from environment variables or config
        """
        # Get configurable settings from config, or use empty dict if not provided
        configurable_settings = config.get("configurable", {}) if config else {}
        
        # Build dictionary of configuration values
        config_values: dict[str, Any] = {}
        
        # Iterate through all dataclass fields
        for field in fields(cls):
            if not field.init:
                continue
            
            field_name = field.name
            env_var_name = field_name.upper()
            
            # Try getting value from:
            # 1. Environment variable
            # 2. Configurable settings
            value = os.environ.get(env_var_name) or configurable_settings.get(field_name)
            
            if value is not None:
                config_values[field_name] = value
        
        # Create new Configuration instance with the collected values
        return cls(**config_values)