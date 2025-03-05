from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from typing_extensions import Annotated, TypedDict
from datetime import datetime
import operator

# Base state class with common fields
@dataclass(kw_only=True)
class BaseState:
    """Base state for all research processes."""
    search_query: str = field(default="")
    web_research_results: Annotated[List[Dict[str, Any]], operator.add] = field(default_factory=list)
    sources_gathered: Annotated[List[str], operator.add] = field(default_factory=list)

# Research-specific state classes
@dataclass(kw_only=True)
class ResearchState(BaseState):
    """State for deep research process."""
    research_topic: str = field(default="")
    research_loop_count: int = field(default=0)
    running_summary: str = field(default="")
    max_iterations: int = field(default=3)

@dataclass(kw_only=True)
class ResearchStateInput:
    """Input state for research process."""
    research_topic: str = field(default="")
    max_iterations: Optional[int] = field(default=None)

@dataclass(kw_only=True)
class ResearchStateOutput:
    """Output state for research process."""
    running_summary: str = field(default="")
    sources_gathered: List[str] = field(default_factory=list)
    research_loop_count: int = field(default=0)

# Newsletter-specific state classes
@dataclass(kw_only=True)
class NewsletterState(BaseState):
    """State for newsletter generation."""
    # Override the search_query field from BaseState to support multiple values
    search_query: Annotated[str, operator.add] = field(default="")
    
    # Input fields
    date: Annotated[str, operator.add] = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    categories: Annotated[List[str], operator.add] = field(default_factory=lambda: [
        "Big Tech & Startups",
        "Science & Futuristic Technology", 
        "Programming, Design & Data Science"
    ])
    
    # Processing state
    current_category: Annotated[Optional[str], operator.add] = None
    search_tool_name: str = field(default="duckduckgo")
    
    # Output fields
    category_summaries: Dict[str, List[Dict]] = field(default_factory=dict)
    tldr_summary: str = field(default="")

@dataclass(kw_only=True)
class NewsletterStateInput:
    """Input state for newsletter generation."""
    date: Optional[str] = field(default=None)
    categories: Optional[List[str]] = field(default=None)
    category_summaries: Optional[Dict[str, List[Dict[str, str]]]] = field(default=None)
    tldr_summary: Optional[str] = field(default=None)
    sources_gathered: Optional[List[str]] = field(default=None)
    current_category: Optional[str] = field(default=None)
    search_query: Optional[str] = field(default=None)
    web_research_results: Optional[List[Dict[str, Any]]] = field(default=None)
    search_tool_name: Optional[str] = field(default=None)

@dataclass(kw_only=True)
class NewsletterStateOutput:
    """Output state for newsletter generation."""
    tldr_summary: str
    category_summaries: Dict = field(default_factory=dict)
    sources_gathered: List = field(default_factory=list)

# For backward compatibility
SummaryState = ResearchState
SummaryStateInput = ResearchStateInput
SummaryStateOutput = ResearchStateOutput 