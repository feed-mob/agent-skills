# Report Template

This template defines the structure of generated intelligence reports.

## Template Variables

| Variable | Description |
|----------|-------------|
| `{topic}` | Topic name (capitalized) |
| `{date}` | Report date (YYYY-MM-DD) |
| `{sources_count}` | Number of active sources |
| `{articles_count}` | Total articles found |
| `{promoted_count}` | Articles meeting threshold |
| `{threshold}` | Minimum score threshold |
| `{insights_table}` | Markdown table of core insights |
| `{detailed_analysis}` | Detailed analysis sections |
| `{source_quality_table}` | Source quality status |
| `{keyword_adjustments}` | Suggested keyword changes |
| `{pending_actions}` | Actions awaiting user approval |

## Report Structure

```markdown
# {topic} Intelligence Report

**Date:** {date}  
**Sources Scanned:** {sources_count} | **Articles Found:** {articles_count} | **Promoted (>={threshold}):** {promoted_count}

---

## Core Insights

> Top insights from all promoted articles

{insights_table}

---

## Detailed Analysis

{detailed_analysis}

---

## Self-Evolution

### Source Quality Update

{source_quality_table}

### Keyword Adjustments

{keyword_adjustments}

---

## Pending Actions

{pending_actions}
```

## Section Guidelines

### Core Insights

- Maximum 10 insights
- Each insight is the first core point from a promoted article
- "New?" column shows Yes for newly discovered insights
- Sorted by relevance score (highest first)

### Detailed Analysis

- One section per promoted article
- Includes: Score, Source, Core Points, Reasoning, Link
- Maximum 5 core points per article
- "[NEW]" badge for new insights

### Self-Evolution

- Shows all active and candidate sources
- Quality score = promoted_articles / total_articles
- Status indicators:
  - Active: Well-performing source
  - Warning: Low quality, monitoring
  - Candidate: Awaiting validation
  - Pruned: Removed from rotation

### Pending Actions

- Checklist format for user actions
- Sources to promote: Candidates meeting quality threshold
- Sources to review: Low-performing active sources
- Keywords to add: Frequently appearing terms in high-scoring articles

## Example Output

```markdown
# AI Agents Intelligence Report

**Date:** 2026-03-23  
**Sources Scanned:** 12 | **Articles Found:** 45 | **Promoted (>=7):** 18

---

## Core Insights

> Top insights from all promoted articles

| # | Insight | Source | New? |
|---|---------|--------|------|
| 1 | OpenAI releases GPT-5 with improved tool use capabilities | OpenAI Blog | Yes |
| 2 | Anthropic introduces Claude 3.5 Sonnet with agentic reasoning | Anthropic | Yes |
| 3 | Google DeepMind achieves breakthrough in agent planning | DeepMind | No |

---

## Detailed Analysis

### OpenAI releases GPT-5 with improved tool use capabilities

**Score:** 9/10 | **Source:** OpenAI Blog | **New Insight:** Yes **[NEW]**

**Core Points:**
- GPT-5 introduces native tool calling without prompting
- 40% improvement in multi-step reasoning tasks
- New "agent mode" for autonomous operation

**Why Relevant:** Major advancement in LLM capabilities for agentic workflows.

**Link:** [https://openai.com/blog/gpt-5](https://openai.com/blog/gpt-5)

---

## Self-Evolution

### Source Quality Update

| Source | Avg Score | Status | Action |
|--------|-----------|--------|--------|
| OpenAI Blog | 0.85 | Active | Maintained |
| Anthropic | 0.82 | Active | Maintained |
| TechCrunch AI | 0.45 | Warning | Monitor |
| AI News Weekly | 0.28 | Pruned | Removed |

### Keyword Adjustments

- **Added:** tool calling, agent mode, planning
- **Reasoning:** Frequently appearing in high-scoring articles

---

## Pending Actions

- [ ] **Sources to promote:** 1 candidate(s) awaiting approval
  - AI Weekly (score: 0.75)
- [ ] **Keywords to add:** 3 suggestion(s)
  - tool calling, agent mode, planning
```