# Common Module

This directory contains shared code that is reused across different components of the application.

## Components

- `state.py` - Shared state classes for research and newsletter functionality
- `search_tools.py` - Search functions and tools for web research
- `source_utils.py` - Utilities for formatting and processing search results
- `llm.py` - Shared LLM configuration and access
- `prompts.py` - Shared prompt templates

## Usage

Import the required components from the common module rather than duplicating functionality. For example:

```python
from ..common.state import ResearchState
from ..common.search_tools import get_search_tool
from ..common.prompts import query_writer_instructions
```

## Structure

The common module follows a modular approach where each file has a clear, single responsibility. This helps with maintainability and makes it easier to find and reuse code.

## Extending

When adding new functionality, consider if it might be useful across different parts of the application. If so, add it to an existing common module or create a new one as appropriate. 