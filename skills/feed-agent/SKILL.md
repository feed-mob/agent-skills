---
name: feed-agent
description: |
  Autonomous RSS/content aggregator with self-evolution capabilities.
  Use this skill when the user wants to:
  - Discover and track topic-specific news from multiple sources
  - Get AI-filtered intelligence reports (score-based filtering)
  - Automatically find new relevant sources for a topic
  - Track information sources over time with quality scoring
  
  Triggers: /feed-agent, "track news about X", "monitor topic", "set up feed for X", "daily intelligence report", "discover sources", "what's new in X"
---

# Feed Agent

An autonomous intelligence aggregator that discovers, filters, and analyzes topic-specific content with self-evolution capabilities.

![Feed Agent Workflow](diagrams/feed-agent-workflow.png)

## Commands

| Command | Description |
|---------|-------------|
| `/feed-agent [topic]` | Run full pipeline: scout → fetch → analyze → report |
| `/feed-agent set-topic [topic]` | Configure the tracking topic |
| `/feed-agent scout` | Run discovery only (find new sources) |
| `/feed-agent report` | Generate report from cached data |
| `/feed-agent sources` | List active and candidate sources |
| `/feed-agent evolve` | Run self-evolution (prune/promote sources) |

## Workflow: `/feed-agent [topic]`

### Step 1: Load Configuration

```bash
python3 scripts/pipeline.py --project-root . --action init --topic "{topic}"
```

Reads `config/feed-agent.yaml` for:
- Active topic
- Enabled search providers
- Scoring thresholds
- Evolution settings

### Step 2: Scout (Discovery)

Run source discovery using enabled search providers:

```bash
python3 scripts/scout.py --project-root . --topic "{topic}"
```

Uses the SearchProvider interface to:
1. Search for "{topic} RSS feeds" and "{topic} news sources"
2. Validate candidate URLs (must return valid RSS/HTML)
3. Score candidates by relevance (LLM-based)
4. Store candidates in `sources/feeds/{topic}/candidates.json`

### Step 3: Fetch (Content Collection)

Fetch full content from all active sources:

```bash
python3 scripts/fetcher.py --project-root . --topic "{topic}"
```

For each source:
1. Fetch RSS feed or scrape web page
2. Extract full article content using webfetch
3. Normalize content (strip HTML, extract text)
4. Store raw items in database

### Step 4: Analyze (AI Scoring)

Score and filter articles:

```bash
python3 scripts/analyzer.py --project-root . --topic "{topic}"
```

For each article:
1. Calculate relevance score (0-10) against topic
2. Compare against historical reports for deduplication
3. Extract core points and insights
4. Mark as "new insight" or "continuation"
5. Store analysis in database

Articles scoring < 7 are filtered out.

### Step 5: Generate Report

Create markdown intelligence report:

```bash
python3 scripts/reporter.py --project-root . --topic "{topic}" --output reports/{topic}/{date}.md
```

Output structure:
- Core Insights (Top insights from promoted articles)
- Detailed Analysis (Full analysis of each article)
- Self-Evolution (Source quality updates and keyword adjustments)

### Step 6: Self-Evolve

Update source quality and keywords:

```bash
python3 scripts/evolution.py --project-root . --topic "{topic}"
```

Based on average scores:
- High-quality sources (> 0.7 avg): Promote in priority
- Low-quality sources (< 0.3 avg): Flag for pruning after N consecutive runs
- Extract suggested keywords from high-scoring articles

## Workflow: `/feed-agent set-topic [topic]`

Initialize or update topic configuration:

```bash
python3 scripts/pipeline.py --project-root . --action config --topic "{topic}"
```

Creates/updates:
- `config/feed-agent.yaml` - Topic and provider settings
- `sources/feeds/{topic}/active.yaml` - Active source list
- Database entry for the topic

## Workflow: `/feed-agent scout`

Run discovery phase only:

```bash
python3 scripts/scout.py --project-root . --topic "{topic}" --verbose
```

Outputs discovered candidates to console and saves to `candidates.json`.

## Workflow: `/feed-agent sources`

List source status:

```bash
python3 scripts/db.py --project-root . --topic "{topic}" list-sources
```

Shows:
- Active sources with quality scores
- Candidate sources pending validation
- Pruned sources (if any)

## Workflow: `/feed-agent evolve`

Force evolution check:

```bash
python3 scripts/evolution.py --project-root . --topic "{topic}" --force
```

## Search Providers

Feed Agent uses a pluggable search provider system. See `references/search-providers.md` for implementation guide.

### Available Providers

| Provider | Tool | Description |
|----------|------|-------------|
| `exa` | `exa_web_search_exa` | Primary - high-quality web search |
| `browser` | `agent-browser` | Secondary - scrapes Google/Brave results |

### Provider Configuration

```yaml
providers:
  enabled:
    - exa
    - browser
  
  exa:
    max_results: 10
    use_autosuggestions: true
  
  browser:
    headless: true
    timeout: 30
```

## AI Scoring

Each article is scored 0-10 for relevance to the configured topic. See `references/scoring-prompts.md` for the complete scoring prompt template.

### Scoring Guide

| Score | Interpretation |
|-------|----------------|
| 9-10 | Directly addresses topic, major new development |
| 7-8 | Highly relevant, contributes meaningful insight |
| 5-6 | Somewhat related, tangential relevance |
| 3-4 | Peripheral connection, low signal |
| 0-2 | Not relevant to topic |

### Historical Comparison

The analyzer checks if an article's core points have been covered in previous reports:
- **New insight**: Not covered in last 30 days
- **Continuation**: Updates or extends previous coverage
- **Duplicate**: Same content from different source (filtered)

## Self-Evolution

The agent continuously improves its source list:

### Source Quality Tracking

```sql
-- Every run updates source quality scores
UPDATE feed_agent_sources 
SET quality_score = promoted_articles / total_articles,
    relevance_avg = AVG(recent_scores)
WHERE topic = ?
```

### Auto-Promotion

Candidates with > 70% promoted articles after 3 validation runs are automatically added to the active source list.

### Auto-Pruning

Sources with < 30% relevance average over 3 consecutive runs are flagged for removal. User must confirm pruning.

### Keyword Evolution

High-scoring articles are analyzed for frequently occurring terms not in the current keyword list. These are stored in the database as candidate keywords, promoted to active when they repeatedly appear in strong articles, and then reused to drive feed discovery queries and relevance scoring.

### Keyword States

- `active` - Used by scout query generation and analysis prompts
- `candidate` - Suggested by analysis, waiting for more evidence
- `rejected` - Suppressed from future reuse

## Report Format

Generated reports follow the template in `references/report-template.md`:

```markdown
# {Topic} Intelligence Report
**Date:** {date}  
**Sources Scanned:** {count} | **Articles Found:** {count} | **Promoted (>=7):** {count}

## Core Insights

> Top insights from all promoted articles

| # | Insight | Source | New? |
|---|---------|--------|------|
| 1 | {insight} | {source} | Yes |

## Detailed Analysis

### {Article Title}
**Score:** {score}/10 | **Source:** {source_name} | **New Insight:** {is_new}

**Core Points:**
- {point_1}
- {point_2}

**Link:** {url}

---

## Self-Evolution

### Source Quality Update
| Source | Avg Score | Status | Action |
|--------|-----------|--------|--------|
| {name} | 0.82 | Active | Maintained |

### Keyword Adjustments
- **Added:** {keywords}
- **Reasoning:** {reason}
```

## Database Schema

See `scripts/db.py` for schema definitions. Key tables:

- `feed_agent_sources` - Source registry with quality tracking
- `feed_agent_articles` - Article storage with analysis
- `feed_agent_evolution_log` - Track all evolution actions

## Dependencies

```bash
pip install feedparser beautifulsoup4 aiohttp pyyaml
```

## Example Usage

```
User: /feed-agent "AI Agents"

Action:
1. Check if topic "AI Agents" is configured
2. Run scout to discover new sources
3. Fetch content from all active sources
4. Analyze and score articles (0-10)
5. Filter (keep ≥ 7)
6. Generate report at reports/ai-agents/2026-03-23.md
7. Run evolution to update source quality
8. Display summary to user
```

## Resource Requirements

When invoking this skill, AI agents should be aware of the following runtime characteristics:

- **Typical time:** 3-10 minutes depending on source count and network conditions
- **Network:** Heavy (multiple RSS fetches, web searches, and content extraction)
- **Recommended timeout:** `timeoutSeconds: 600` (10 minutes) minimum
- **Token usage:** ~500k-1M tokens per full pipeline run

This is a long-running batch task. Do not expect synchronous results; use appropriate async patterns (e.g., `sessions_yield`, background sessions) when calling.

## Error Handling

| Error | Response |
|-------|----------|
| No sources configured | Guide user to run `/feed-agent set-topic` first |
| All articles filtered | Report mentions filter rate, suggest lowering threshold |
| No new articles | Check `last_fetched` timestamp, report stale sources |
| Scout finds no candidates | User may need to adjust topic keywords |
