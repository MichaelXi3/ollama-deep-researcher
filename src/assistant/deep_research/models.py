from typing import List
from dataclasses import dataclass

@dataclass
class ResearchResult:
    """Result of deep research."""
    summary: str
    key_findings: List[str]
    sources: List[str] 