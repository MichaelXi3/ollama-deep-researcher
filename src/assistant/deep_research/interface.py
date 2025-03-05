from typing import Dict, Any, Optional
from langchain_core.runnables import RunnableConfig

from .graph import create_research_graph
from .state import ResearchState
from .models import ResearchResult

class DeepResearcher:
    """Interface for deep research capabilities."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the deep researcher."""
        self.config = config or {}
        self.runnable_config = RunnableConfig(self.config)
        self.research_graph = create_research_graph(self.runnable_config)
    
    async def research_topic(self, topic: str, depth: int = 3) -> ResearchResult:
        """Research a topic in depth.
        
        Args:
            topic: The topic to research
            depth: How deep to go in the research (number of iterations)
            
        Returns:
            ResearchResult containing summary and key findings
        """
        # Create research state
        state = ResearchState(
            research_topic=topic,
            max_iterations=depth
        )
        
        # Run the research graph
        result = await self.research_graph.ainvoke(state)
        
        # Extract key findings from the summary
        import re
        findings = []
        summary = result.running_summary
        
        # Look for bullet points or numbered lists in the summary
        bullet_pattern = r"[•\-\*]\s*(.*?)(?=(?:[•\-\*]|\Z))"
        numbered_pattern = r"\d+\.\s*(.*?)(?=(?:\d+\.|\Z))"
        
        # Try to find bullet points first
        findings = re.findall(bullet_pattern, summary, re.DOTALL)
        
        # If no bullet points found, try numbered list
        if not findings:
            findings = re.findall(numbered_pattern, summary, re.DOTALL)
        
        # If still no findings, split by newlines and take non-empty lines
        if not findings:
            findings = [line.strip() for line in summary.split('\n') if line.strip()]
        
        # Clean up findings
        findings = [f.strip() for f in findings if f.strip()]
        
        return ResearchResult(
            summary=summary,
            key_findings=findings[:5],  # Take top 5 findings
            sources=result.sources_gathered
        ) 