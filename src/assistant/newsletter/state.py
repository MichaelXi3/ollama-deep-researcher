from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class NewsletterState:
    """State for newsletter generation."""
    
    # Input fields
    date: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    
    # Processing state
    current_category: Optional[str] = None
    search_query: str = ""
    web_research_results: List[Dict] = field(default_factory=list)
    search_tool_name: str = "duckduckgo"
    
    # Output fields
    category_summaries: Dict[str, List[Dict]] = field(default_factory=dict)
    newsletter_summary: str = ""
    sources_gathered: List[str] = field(default_factory=list)

@dataclass(kw_only=True)
class NewsletterStateInput:
    """Input state for newsletter generation."""
    date: Optional[str] = field(default=None)
    categories: Optional[List[str]] = field(default=None)
    category_summaries: Optional[Dict[str, List[Dict[str, str]]]] = field(default=None)
    newsletter_summary: Optional[str] = field(default=None)
    sources_gathered: Optional[List[str]] = field(default=None)
    current_category: Optional[str] = field(default=None)
    search_query: Optional[str] = field(default=None)
    web_research_results: Optional[List[Dict[str, str]]] = field(default=None)
    search_tool_name: Optional[str] = field(default=None)

@dataclass(kw_only=True)
class NewsletterStateOutput:
    """Output state for newsletter generation."""
    newsletter_summary: str
    category_summaries: Dict = field(default_factory=dict)
    sources_gathered: List = field(default_factory=list) 