# Search Provider Implementation Guide

This guide explains how to implement new search providers for the Feed Agent.

## Provider Interface

All search providers must extend the `SearchProvider` base class from `search_provider.py`:

```python
from search_provider import SearchProvider, SearchResult, FeedCandidate, SourceType

class MyProvider(SearchProvider):
    @property
    def name(self) -> str:
        return "my_provider"
    
    def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        # Implement search
        pass
    
    def discover_feeds(self, topic: str, max_results: int = 5) -> List[FeedCandidate]:
        # Implement feed discovery
        pass
```

## SearchResult

```python
@dataclass
class SearchResult:
    url: str                    # URL of the result
    title: str                  # Title/headline
    snippet: str                # Brief description
    source_type: SourceType     # RSS, BLOG, NEWS, or UNKNOWN
    relevance_hint: float      # Optional relevance score (0-1)
```

## FeedCandidate

```python
@dataclass
class FeedCandidate:
    url: str                    # Feed URL
    name: str                   # Feed name/title
    source_type: SourceType     # RSS, BLOG, NEWS, or UNKNOWN
    discovered_from: str        # Provider name or "manual"
    confidence: float           # Confidence in relevance (0-1)
```

## Implementation Pattern

Most providers follow this pattern:

1. **Return instructions to the agent** (not execute directly)
2. **Process tool output** when provided by the agent
3. **Validate feed URLs** before returning candidates

### Example: Exa Provider

```python
class ExaAdapter(SearchProvider):
    def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        # Return empty - agent uses exa_web_search_exa tool directly
        return []
    
    def search_with_results(self, tool_output: dict, topic: str) -> List[SearchResult]:
        # Process the tool output
        results = []
        for item in tool_output.get("results", []):
            results.append(SearchResult(
                url=item["url"],
                title=item["title"],
                snippet=item.get("content", ""),
                source_type=self._detect_source_type(item["url"], "")
            ))
        return results
```

## Source Type Detection

Implement `_detect_source_type(self, url: str, content: str)` to classify sources:

```python
def _detect_source_type(self, url: str, content: str) -> SourceType:
    url_lower = url.lower()
    
    # Check for RSS indicators
    if any(x in url_lower for x in ["/feed", "/rss", "/atom"]):
        return SourceType.RSS
    
    # Check for blog indicators
    if "blog" in url_lower:
        return SourceType.BLOG
    
    # Check for news indicators
    if any(x in url_lower for x in ["news", "breaking"]):
        return SourceType.NEWS
    
    return SourceType.UNKNOWN
```

## Adding a New Provider

1. Create `my_provider.py` in `scripts/`
2. Implement the `SearchProvider` interface
3. Add to `config/feed-agent.yaml`:

```yaml
providers:
  enabled:
    - exa
    - browser
    - my_provider
  
  my_provider:
    api_key: ${MY_PROVIDER_API_KEY}
    max_results: 10
```

4. Update `scout.py` to handle the new provider

## Testing Providers

```bash
# Test search queries
python3 scripts/my_provider.py --topic "AI Agents" --action queries

# Validate a feed URL
python3 scripts/search_provider.py --validate "https://example.com/feed"
```

## Built-in Providers

| Provider | Tool | Description |
|----------|------|-------------|
| `exa` | `exa_web_search_exa` | AI-optimized web search |
| `browser` | `agent-browser` | Web scraping fallback |