"""Newsletter generation graph.

This module provides a specialized graph for newsletter generation that can:
1. Process multiple news categories
2. Generate category-specific summaries
3. Create Builder's News summaries
4. Handle multiple search providers (DuckDuckGo, Tavily, Perplexity)

The graph maintains state between different stages of newsletter generation
and can be configured to use different search tools and LLM models."""

from datetime import datetime
import json
from typing import Optional
import traceback

from langgraph.graph import Graph, StateGraph
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig

from ..common.search_tools import get_search_tool
from ..common.llm import get_llm
from .state import NewsletterState
from ..common.prompts import (
    newsletter_query_instructions,
    newsletter_summarizer_instructions,
    newsletter_generator_instructions,
)

def create_newsletter_graph(
    config: RunnableConfig,
) -> Graph:
    """Create a graph for newsletter generation."""
    
    # Initialize tools
    search_tool_name = config.get("search_tool", "duckduckgo")
    search_tool = get_search_tool(search_tool_name)
    tools = [search_tool]

    # Initialize LLM
    llm = get_llm(config)
    
    def initialize_state(state: NewsletterState) -> NewsletterState:
        """Initialize the newsletter state with required fields."""
        # Print to terminal for visibility
        print("\n=== Initializing Newsletter State ===")
        
        # Preserve input state values if they exist
        if not state.date:
            state.date = datetime.now().strftime("%Y-%m-%d")
        if not state.categories:
            state.categories = [
                "Big Tech & Startups",
                "Science & Futuristic Technology", 
                "Programming, Design & Data Science"
            ]
        if not state.current_category:
            state.current_category = state.categories[0]
            
        # Always initialize these
        state.category_summaries = {}
        state.newsletter_summary = ""
        state.sources_gathered = []
        state.search_query = ""
        state.web_research_results = []
        state.search_tool_name = search_tool_name
        
        # Print state information
        print(f"Date: {state.date}")
        print(f"Categories: {state.categories}")
        print(f"Starting Category: {state.current_category}")
        print(f"Search Tool: {search_tool_name}")
        
        return state

    def generate_search_query(state: NewsletterState) -> NewsletterState:
        """Generate search query for current category."""
        print(f"\n=== Generating Search Query for {state.current_category} ===")
        
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", newsletter_query_instructions),
                MessagesPlaceholder(variable_name="history"),
                ("human", "Generate a search query for the specified category and date."),
            ])
            
            chain = prompt | llm
            
            response = chain.invoke({
                "category": state.current_category,
                "date": state.date,
                "history": [],
            })
            
            query_data = json.loads(response.content)
            state.search_query = query_data["query"]
            print(f"Generated Query: {state.search_query}")
        except Exception as e:
            error = f"Failed to generate search query: {str(e)}"
            print(error)
            print(traceback.format_exc())
            # Set a default query to prevent workflow from breaking
            state.search_query = f"{state.current_category} latest news {state.date}"
            print(f"Using fallback query: {state.search_query}")
        
        return state

    async def search_news(state: NewsletterState) -> NewsletterState:
        """Search for news articles using configured tools."""
        # Log to terminal
        message = f"""
=== Category Processing Status ===
Current Category: {state.current_category}
Search Query: {state.search_query}
"""
        print(message)
        
        try:
            # Regular web search
            print("Executing web search...")
            search_results = await tools[0].ainvoke(
                state.search_query,
                config=config
            )
            
            # Store the raw search results
            state.web_research_results = search_results
            result_count = len(search_results.get('results', []))
            status = f"Found {result_count} search results"
            print(status)
            
            # Extract URLs from the results dictionary
            if isinstance(search_results, dict) and "results" in search_results:
                urls = [r["url"] for r in search_results["results"]]
                state.sources_gathered.extend(urls)
                sources = f"Sources gathered: {urls}"
                print(sources)
            
        except Exception as e:
            error = f"Search failed: {str(e)}"
            print(error)
            print(traceback.format_exc())
            # Initialize empty results if search fails
            state.web_research_results = {"results": []}
            
        return state

    def summarize_category(state: NewsletterState) -> NewsletterState:
        """Summarize search results for current category."""
        print(f"\n=== Summarizing {state.current_category} ===")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", newsletter_summarizer_instructions),
            MessagesPlaceholder(variable_name="history"),
            ("human", "Summarize the search results for this category."),
        ])
        
        chain = prompt | llm
        
        # Prepare the input for the summarizer
        summarizer_input = {
            "category": state.current_category,
            "history": [],
            "web_research_results": state.web_research_results,
        }
        
        response = chain.invoke(summarizer_input)
        
        try:
            summary_data = json.loads(response.content)
            state.category_summaries[state.current_category] = summary_data["summaries"]
            print(f"Generated {len(summary_data['summaries'])} article summaries")
        except Exception as e:
            error = f"Failed to parse summary: {str(e)}"
            print(error)
            state.category_summaries[state.current_category] = []
        
        return state

    def generate_newsletter(state: NewsletterState) -> NewsletterState:
        """Generate Builder's News summary of all categories."""
        print("\n=== Generating Builder's News Summary ===")
        
        # Check if all categories have been processed
        for category in state.categories:
            if category not in state.category_summaries:
                print(f"Warning: Category '{category}' was not processed. Adding empty summary.")
                state.category_summaries[category] = []
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", newsletter_generator_instructions),
            MessagesPlaceholder(variable_name="history"),
            ("human", "Create a Builder's News summary of today's tech news."),
        ])
        
        chain = prompt | llm
        
        # Create category emoji mapping
        category_emojis = {
            "Big Tech & Startups": "📱",
            "Science & Futuristic Technology": "🚀",
            "Programming, Design & Data Science": "💻"
        }
        
        # Format the newsletter
        newsletter = f"🏗️ Builder's News {state.date}\n\n"
        
        # Add each category section
        for category in state.categories:
            emoji = category_emojis.get(category, "")
            newsletter += f"{emoji}\n{category}\n"
            
            # Add each article in the category
            for article in state.category_summaries.get(category, []):
                newsletter += f"{article['title']}\n\n"
                newsletter += f"{article['summary']}\n"
                newsletter += f"Read more: {article['url']}\n\n"
            
        state.newsletter_summary = newsletter
        print("Builder's News summary generated")
        
        return state

    def update_category(state: NewsletterState) -> NewsletterState:
        """Move to the next category if available."""
        try:
            current_index = state.categories.index(state.current_category)
            
            if current_index + 1 < len(state.categories):
                next_category = state.categories[current_index + 1]
                print(f"\nMoving to next category: {next_category}")
                state.current_category = next_category
                # Reset search-related state for the new category
                state.search_query = ""
                state.web_research_results = []
            else:
                print("\nNo more categories to process")
        except Exception as e:
            print(f"Error in update_category: {str(e)}")
            print(traceback.format_exc())
            # If we can't update properly, we'll stay on the current category
        
        return state

    def should_process_next_category(state: NewsletterState) -> bool:
        """Check if there are more categories to process."""
        try:
            # Check if we've processed a reasonable number of categories through the normal flow
            # This prevents infinite loops and ensures we eventually move to the cleanup phase
            processed_categories = len([cat for cat in state.categories if cat in state.category_summaries])
            max_normal_processing = min(len(state.categories), 2)  # Process at most 2 categories normally
            
            if processed_categories >= max_normal_processing:
                print(f"Processed {processed_categories}/{len(state.categories)} categories normally, moving to cleanup phase")
                return False
                
            # Check if we're on the last category
            current_index = state.categories.index(state.current_category)
            has_more = current_index + 1 < len(state.categories)
            print(f"Checking if more categories: current={state.current_category}, index={current_index}, has_more={has_more}")
            return has_more
        except Exception as e:
            print(f"Error in should_process_next_category: {str(e)}")
            print(traceback.format_exc())
            # Default to False to avoid infinite loops
            return False
    
    def end_workflow(state: NewsletterState) -> NewsletterState:
        """End the workflow and return the final state."""
        print("\n=== Newsletter Generation Complete ===")
        return state

    # Create the graph
    workflow = StateGraph(NewsletterState)

    # Add nodes
    workflow.add_node("initialize", initialize_state)
    workflow.add_node("generate_query", generate_search_query)
    workflow.add_node("search", search_news)
    workflow.add_node("summarize", summarize_category)
    workflow.add_node("update_category", update_category)
    workflow.add_node("generate_newsletter", generate_newsletter)
    workflow.add_node("end", end_workflow)
    
    # Add a special node for processing any remaining categories
    def process_remaining_categories(state: NewsletterState) -> NewsletterState:
        """Process any categories that haven't been processed yet."""
        # Find categories that haven't been processed
        unprocessed_categories = [cat for cat in state.categories if cat not in state.category_summaries]
        
        if unprocessed_categories:
            print(f"\n=== Processing Remaining Categories ({len(unprocessed_categories)}) ===")
            
            # Process each remaining category
            for category in unprocessed_categories:
                print(f"\n=== Special Processing for {category} ===")
                state.current_category = category
                state.search_query = f"{category} latest news {state.date}"
                print(f"Setting search query: {state.search_query}")
                
                # Perform search
                try:
                    print("Executing web search...")
                    search_results = tools[0].invoke(
                        state.search_query,
                        config=config
                    )
                    
                    # Store the raw search results
                    state.web_research_results = search_results
                    result_count = len(search_results.get('results', []))
                    status = f"Found {result_count} search results"
                    print(status)
                    
                    # Extract URLs from the results dictionary
                    if isinstance(search_results, dict) and "results" in search_results:
                        urls = [r["url"] for r in search_results["results"]]
                        state.sources_gathered.extend(urls)
                        sources = f"Sources gathered: {urls}"
                        print(sources)
                    
                    # Summarize the results
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", newsletter_summarizer_instructions),
                        MessagesPlaceholder(variable_name="history"),
                        ("human", "Summarize the search results for this category."),
                    ])
                    
                    chain = prompt | llm
                    
                    # Prepare the input for the summarizer
                    summarizer_input = {
                        "category": state.current_category,
                        "history": [],
                        "web_research_results": state.web_research_results,
                    }
                    
                    response = chain.invoke(summarizer_input)
                    
                    try:
                        summary_data = json.loads(response.content)
                        state.category_summaries[state.current_category] = summary_data["summaries"]
                        print(f"Generated {len(summary_data['summaries'])} article summaries")
                    except Exception as e:
                        error = f"Failed to parse summary: {str(e)}"
                        print(error)
                        state.category_summaries[state.current_category] = []
                except Exception as e:
                    error = f"Search failed for {category}: {str(e)}"
                    print(error)
                    print(traceback.format_exc())
                    # Initialize empty results if search fails
                    state.web_research_results = {"results": []}
                    state.category_summaries[state.current_category] = []
        else:
            print("All categories have been processed already")
        
        return state
    
    workflow.add_node("process_remaining_categories", process_remaining_categories)

    # Add edges - make the flow more sequential
    workflow.set_entry_point("initialize")
    workflow.add_edge("initialize", "generate_query")
    workflow.add_edge("generate_query", "search")
    workflow.add_edge("search", "summarize")
    workflow.add_edge("summarize", "update_category")
    
    # Use conditional edges to determine next step
    workflow.add_conditional_edges(
        "update_category",
        should_process_next_category,
        {
            True: "generate_query",
            False: "process_remaining_categories"
        }
    )
    
    workflow.add_edge("process_remaining_categories", "generate_newsletter")
    workflow.add_edge("generate_newsletter", "end")

    return workflow.compile()

# Create a default instance of the graph
graph = create_newsletter_graph(RunnableConfig({})) 