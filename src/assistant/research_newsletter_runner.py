from typing import Optional, Dict, Any
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import os

from langchain_core.runnables import RunnableConfig

from .base_research_graph import graph as base_graph
from .newsletter.graph import create_newsletter_graph
from .newsletter.state import NewsletterState

class NewsletterRunner:
    """Runner for newsletter generation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the runner with configuration."""
        # Load environment variables for configuration
        load_dotenv()
        
        self.config = config or {
            "model_name": os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
            "search_tool": os.getenv("SEARCH_TOOL", "duckduckgo"),
        }
        self.runnable_config = RunnableConfig(self.config)
        
        # Create newsletter graph
        self.newsletter_graph = create_newsletter_graph(self.runnable_config)
    
    async def run(
        self,
        categories: Optional[list[str]] = None,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the newsletter generation process.
        
        Args:
            categories: Optional list of categories to process
            date: Optional specific date for the newsletter
            
        Returns:
            Dictionary containing newsletter results
        """
        # Use default categories if none provided
        if not categories:
            categories = [
                "Big Tech & Startups",
                "Science & Futuristic Technology",
                "Programming, Design & Data Science"
            ]
            
        # Prepare input for newsletter
        newsletter_input = NewsletterState(
            date=date or datetime.now().strftime("%Y-%m-%d"),
            categories=categories,
            category_summaries={},
            tldr_summary="",
            sources_gathered=[],
            current_category=categories[0]
        )
            
        # Run the newsletter graph
        result = await self.newsletter_graph.ainvoke(newsletter_input)
        
        # Handle different result types from LangGraph
        if hasattr(result, 'tldr_summary'):
            # Direct access if it's a simple object
            return {
                "tldr_summary": result.tldr_summary,
                "category_summaries": result.category_summaries,
                "sources": result.sources_gathered
            }
        elif isinstance(result, dict):
            # If result is a dict, extract values
            return {
                "tldr_summary": result.get("tldr_summary", ""),
                "category_summaries": result.get("category_summaries", {}),
                "sources": result.get("sources_gathered", [])
            }
        else:
            # For other result types (like AddableValuesDict)
            print(f"Result type: {type(result)}")
            # Try to convert to dict and extract values
            result_dict = dict(result) if hasattr(result, "__iter__") else {}
            return {
                "tldr_summary": result_dict.get("tldr_summary", ""),
                "category_summaries": result_dict.get("category_summaries", {}),
                "sources": result_dict.get("sources_gathered", [])
            }

async def main():
    """Example usage of the runner."""
    runner = NewsletterRunner()
    
    # Run with default settings
    result = await runner.run()
    print("Generated Newsletter:")
    print(result["tldr_summary"])

if __name__ == "__main__":
    asyncio.run(main()) 