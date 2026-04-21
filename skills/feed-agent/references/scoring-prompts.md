# AI Scoring Prompts

This file contains the prompt templates used for article relevance scoring.

## Main Scoring Prompt

```
# Article Relevance Scoring

**Topic:** {topic}
**Article Title:** {title}
**Article Content:** {content}

**Task:**
1. Score this article 0-10 for relevance to "{topic}"
2. Identify if this represents a NEW insight or repetition of known information
3. Extract 3-5 core points (key insights, findings, or developments)
4. Suggest any new keywords that should be tracked for this topic

**Response Format (JSON):**
{
  "score": <integer 0-10>,
  "is_new_insight": <boolean>,
  "story_status": "<new|continuation|duplicate>",
  "core_points": ["point 1", "point 2", "point 3"],
  "reasoning": "<brief explanation of the score>",
  "suggested_keywords": ["keyword1", "keyword2"]
}

**Scoring Guide:**
- 9-10: Directly addresses {topic}, major new development or breakthrough
- 7-8: Highly relevant, contributes meaningful insight or useful information
- 5-6: Somewhat related, tangential relevance, context but not core
- 3-4: Peripheral connection, low signal-to-noise ratio
- 0-2: Not relevant to {topic}, should be filtered out
```

## Historical Comparison Prompt

```
# Historical Comparison

**Topic:** {topic}
**Current Article Core Points:**
{current_points}

**Recent Articles Core Points (last 7 days):**
{historical_points}

**Task:**
Compare the current article's core points against the historical record.
Determine if this is:
- "new": Novel information not covered before
- "continuation": Update or extension of previously reported story
- "duplicate": Same content from a different source (should be filtered)

**Response Format (JSON):**
{
  "classification": "<new|continuation|duplicate>",
  "reasoning": "<brief explanation>",
  "related_article_ids": [<ids of related articles if continuation or duplicate>]
}
```

## Scoring Best Practices

1. **Be strict on relevance**: A score of 7+ should genuinely contribute to understanding the topic
2. **Core points should be specific**: Not "AI is growing" but "OpenAI released GPT-5 with improved reasoning"
3. **Historical comparison is crucial**: Avoid duplicating the same news from different sources
4. **Keywords should be actionable**: Terms that could be added to search queries to find similar content

## Score Interpretation

| Score Range | Interpretation | Action |
|-------------|----------------|--------|
| 9-10 | Major development | Include in Core Insights prominently |
| 7-8 | Relevant insight | Include in Detailed Analysis |
| 5-6 | Context/tangential | Keep for reference, don't highlight |
| 3-4 | Low signal | Filter out |
| 0-2 | Irrelevant | Filter out immediately |
