"""Common prompt templates used across different modules.

This module contains prompt templates that are used by multiple components of the application.
These are shared to maintain consistency and avoid duplication.
"""

# Research prompts
query_writer_instructions = """Your goal is to generate a targeted web search query.
The query will gather information related to a specific topic.

<TOPIC>
{research_topic}
</TOPIC>

<FORMAT>
Format your response as a JSON object with ALL three of these exact keys:
   - "query": The actual search query strxing
   - "aspect": The specific aspect of the topic being researched
   - "rationale": Brief explanation of why this query is relevant
</FORMAT>

<EXAMPLE>
Example output:
{{
    "query": "machine learning transformer architecture explained",
    "aspect": "technical architecture",
    "rationale": "Understanding the fundamental structure of transformer models"
}}
</EXAMPLE>

Provide your response in JSON format:"""

summarizer_instructions = """
<GOAL>
Generate a high-quality summary of the web search results and keep it concise / related to the user topic.
</GOAL>

<REQUIREMENTS>
When creating a NEW summary:
1. Highlight the most relevant information related to the user topic from the search results
2. Ensure a coherent flow of information

When EXTENDING an existing summary:                                                                                                                 
1. Read the existing summary and new search results carefully.                                                    
2. Compare the new information with the existing summary.                                                         
3. For each piece of new information:                                                                             
    a. If it's related to existing points, integrate it into the relevant paragraph.                               
    b. If it's entirely new but relevant, add a new paragraph with a smooth transition.                            
    c. If it's not relevant to the user topic, skip it.                                                            
4. Ensure all additions are relevant to the user's topic.                                                         
5. Verify that your final output differs from the input summary.                                                                                                                                                            
</REQUIREMENTS>

<FORMATTING>
- Start directly with the updated summary, without preamble or titles. Do not use XML tags in the output.  
</FORMATTING>"""

reflection_instructions = """You are an expert research assistant analyzing a summary about {research_topic}.

<GOAL>
1. Identify knowledge gaps or areas that need deeper exploration
2. Generate a follow-up question that would help expand your understanding
3. Focus on technical details, implementation specifics, or emerging trends that weren't fully covered
</GOAL>

<REQUIREMENTS>
Ensure the follow-up question is self-contained and includes necessary context for web search.
</REQUIREMENTS>

<FORMAT>
Format your response as a JSON object with these exact keys:
- knowledge_gap: Describe what information is missing or needs clarification
- follow_up_query: Write a specific question to address this gap
</FORMAT>

<EXAMPLE>
Example output:
{{
    "knowledge_gap": "The summary lacks information about performance metrics and benchmarks",
    "follow_up_query": "What are typical performance benchmarks and metrics used to evaluate [specific technology]?"
}}
</EXAMPLE>

Provide your analysis in JSON format:"""

# Newsletter prompts
newsletter_query_instructions = """You are a tech news curator. Your task is to generate a search query to find the top three latest news articles for a specific tech category.

<CATEGORY>
{category}
</CATEGORY>

<DATE>
{date}
</DATE>

The query should:
1. Focus on the specified category
2. Target news from the specified date
3. Prioritize major developments and announcements
4. Be specific enough to find relevant articles but not too narrow

Output your query in JSON format like this:
{{
    "query": "your search query here"
}}
"""

newsletter_summarizer_instructions = """You are a tech newsletter writer. Your task is to summarize news articles for a specific category.

<CATEGORY>
{category}
</CATEGORY>

<SEARCH_RESULTS>
{web_research_results}
</SEARCH_RESULTS>

For each article in the search results:
1. Create a clear, concise title that captures the main point
2. Estimate reading time (in minutes)
3. Write a concise 1-2 paragraph summary
4. Focus on facts and key developments
5. Maintain a professional, neutral tone

Format each article summary as:
{{
    "title": "Article Title Here (X minute read)",
    "summary": "1-2 paragraph summary here",
    "url": "Article URL here"
}}

Return a list of article summaries in JSON format:
{{
    "summaries": [
        {{article1}},
        {{article2}},
        ...
    ]
}}
"""

newsletter_generator_instructions = """You are a tech newsletter editor. Your task is to create a well-formatted newsletter combining all category summaries.

Use this format:

🏗️ Builder's News {date}

{categories_content}

For each category:
1. Show the category name with its emoji
2. Add a blank line
3. List all articles in that category

For each article:
1. Show the title with reading time
2. Add a blank line
3. Show the summary
4. Add a blank line between articles

Keep summaries concise and informative. Focus on the most important developments in each category.""" 