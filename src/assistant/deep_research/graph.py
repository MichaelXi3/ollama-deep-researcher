"""Deep research graph implementation for in-depth topic analysis.

This specialized graph focuses on:
1. Deep, iterative research on specific topics
2. Knowledge gap identification and follow-up queries
3. Comprehensive source gathering and analysis
4. Integration with the newsletter generation system
5. Advanced summarization and insight generation

The graph uses an iterative approach to build comprehensive understanding
of topics through multiple research cycles."""

from typing import Dict, List, Any
from langgraph.graph import Graph, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig

from ..common.search_tools import get_search_tool
from ..common.source_utils import format_sources
from ..common.llm import get_llm
from ..common.state import ResearchState
from ..common.prompts import query_writer_instructions, summarizer_instructions, reflection_instructions
from .models import ResearchResult

def create_research_graph(config: RunnableConfig) -> Graph:
    """Create a graph for deep research."""
    
    # Initialize tools
    search_tool_name = config.get("search_tool", "duckduckgo")
    search_tool = get_search_tool(search_tool_name)
    tools = [search_tool]

    # Initialize LLM
    llm = get_llm(config)

    # Define nodes
    def initialize_state(state: ResearchState) -> ResearchState:
        """Initialize the research state."""
        state.research_loop_count = 0
        state.web_research_results = []
        state.sources_gathered = []
        state.running_summary = ""
        return state

    def generate_search_query(state: ResearchState) -> ResearchState:
        """Generate a search query based on current state."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", query_writer_instructions),
            ("human", "Generate a search query for this research topic: {research_topic}"),
        ])
        
        chain = prompt | llm
        
        response = chain.invoke({
            "research_topic": state.research_topic,
        })
        
        # Parse the JSON response
        import json
        try:
            query_data = json.loads(response.content)
            state.search_query = query_data["query"]
        except (json.JSONDecodeError, KeyError):
            # Fallback in case of parsing error
            state.search_query = state.research_topic
            
        return state

    def search_web(state: ResearchState) -> ResearchState:
        """Execute web search."""
        search_results = search_tool.invoke(
            state.search_query,
            name="web_search"
        )
        
        state.web_research_results.extend(search_results)
        
        # Extract URLs
        if isinstance(search_results, dict) and "results" in search_results:
            state.sources_gathered.extend([r["url"] for r in search_results["results"]])
        
        return state

    def update_summary(state: ResearchState) -> ResearchState:
        """Update the running summary with new information."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", summarizer_instructions),
            ("human", """Please update or create a summary based on the following:
                
Current summary: {current_summary}

New search results: {new_results}"""),
        ])
        
        chain = prompt | llm
        
        response = chain.invoke({
            "current_summary": state.running_summary or "No existing summary.",
            "new_results": "\n".join(str(result) for result in state.web_research_results),
        })
        
        state.running_summary = response.content
        # Clear processed results
        state.web_research_results = []
        return state

    def reflect_and_identify_gaps(state: ResearchState) -> ResearchState:
        """Reflect on current findings and identify knowledge gaps."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", reflection_instructions),
            ("human", "Analyze the current findings and identify gaps in our research about: {research_topic}. Current summary: {current_summary}"),
        ])
        
        chain = prompt | llm
        
        response = chain.invoke({
            "current_summary": state.running_summary,
            "research_topic": state.research_topic,
        })
        
        # Parse the JSON response
        import json
        try:
            reflection_data = json.loads(response.content)
            state.search_query = reflection_data["follow_up_query"]
        except (json.JSONDecodeError, KeyError):
            # Fallback in case of parsing error
            state.search_query = f"latest developments in {state.research_topic}"
        
        # Update iteration count
        state.research_loop_count += 1
        return state

    # Create the graph with schemas
    workflow = StateGraph(
        ResearchState,
        input=ResearchState,
        output=ResearchState,
        config_schema=RunnableConfig
    )

    # Add nodes
    workflow.add_node("initialize", initialize_state)
    workflow.add_node("generate_query", generate_search_query)
    workflow.add_node("search_web", search_web)
    workflow.add_node("update_summary", update_summary)
    workflow.add_node("reflect", reflect_and_identify_gaps)

    # Add edges
    workflow.add_edge("initialize", "generate_query")
    workflow.add_edge("generate_query", "search_web")
    workflow.add_edge("search_web", "update_summary")
    workflow.add_edge("update_summary", "reflect")
    
    # Conditional edges
    def should_continue_research(state: ResearchState) -> bool:
        """Determine if more research is needed."""
        return state.research_loop_count < state.max_iterations

    # Add conditional edges
    workflow.add_conditional_edges(
        "reflect",
        should_continue_research,
        {
            True: "search_web",
            False: "update_summary"
        }
    )

    # Set entry point
    workflow.set_entry_point("initialize")

    # Compile the graph
    app = workflow.compile()
    return app

# Create a default instance of the graph
graph = create_research_graph(RunnableConfig({})) 