# Agent Skills

A collection of skills for Claude agents to perform specialized tasks.

## What Are Skills?

**Skills** are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. They teach Claude how to complete specific tasks in a repeatable way.

## Available Skills

This repository contains 6 specialized skills organized by domain:

### 🎨 Content Creation & Brand Management

#### [feedmob-brand-guidelines](skills/feedmob-brand-guidelines/)
Generate FeedMob-branded content including reports, presentations, charts, and artifacts following official brand guidelines.

**Key Features:**
- Complete FeedMob brand identity system (colors, typography, logos)
- Professional design guidelines for reports and presentations
- Data visualization standards with consistent color mapping
- Logo usage specifications and asset management
- Quality checklists for brand compliance

**Use when:** Creating any FeedMob-branded materials, reports, presentations, charts, or marketing content.

#### [feedmob-presentations](skills/feedmob-presentations/)
Create, edit, and analyze PowerPoint presentations with professional styling, themes, and layouts using python-pptx and OOXML manipulation.

**Key Features:**
- Multiple color schemes (FeedMob, Binance, Professional, Modern, Corporate)
- Automatic background selection based on content
- Smart logo insertion and brand consistency
- Advanced slide types (metrics dashboards, comparisons, two-column layouts)
- Direct OOXML editing for complex modifications
- Design principles implementation (6x6 rule, typography standards, grid alignment)

**Use when:** Creating or editing PowerPoint presentations, especially for FeedMob or professional business contexts.

### 📊 Data Analysis & Processing

#### [civitai-analyst](skills/civitai-analyst/)
Generate and execute SQL queries against the civitai_records PostgreSQL database to analyze video performance on Civitai platform.

**Key Features:**
- Natural language to SQL query generation
- Engagement metrics analysis (likes, hearts, comments)
- Tag and theme performance analysis
- Weekly report generation (JSON/HTML formats)
- WoW (week-over-week) comparison analysis
- Bilingual support (English/中文)

**Use when:** Analyzing Civitai video performance, engagement metrics, content strategy, or generating weekly reports.

**Triggers:** Civitai, video stats, engagement, likes, hearts, comments, weekly report, tag analysis, quality score, 数据分析, 视频表现, 周报

#### [url-parameter-parser](skills/url-parameter-parser/)
Parse URLs in CSV files and extract query parameters as new columns for data analysis.

**Key Features:**
- Automatic URL column detection
- Query parameter extraction and column creation
- Multiple value handling (joined with '|')
- Batch processing of multiple CSV files
- Preserves original data integrity

**Use when:** Working with CSV files containing URLs that need parameter extraction and analysis.

### 🤖 AI & Media Generation

#### [gemini-image-generator](skills/gemini-image-generator/)
Generate, edit, or transform images using Gemini AI (Flash or Pro models) with support for various aspect ratios, resolutions, and image-to-image transformations.

**Key Features:**
- Text-to-image generation with customizable aspect ratios
- Image editing and image-to-image transformations
- Logo overlay capabilities
- Reference image support (up to 14 images on Pro)
- Multiple resolution options (1K, 2K, 4K on Pro)
- Aspect ratio support: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9

**Use when:** Generating images from text, editing existing images, placing logos, or creating image variations.

#### [ai-news-daily](skills/ai-news-daily/)
Automatically fetch and summarize the latest AI news, research, and industry developments from multiple authoritative sources.

**Key Features:**
- Multi-source news aggregation (TechCrunch, VentureBeat, arXiv, etc.)
- Categorized search (general news, research papers, company announcements, market trends)
- Customizable output formats (brief, detailed, report)
- Time-based filtering (daily, weekly updates)
- Source quality prioritization
- Topic-specific deep dives

**Use when:** Requesting daily AI news updates, latest AI research, industry trends, or automated briefings.

## Skill Compatibility Matrix

Some skills work exceptionally well together. Here are recommended combinations:

| Primary Skill | Compatible With | Use Case |
|---------------|----------------|----------|
| **feedmob-presentations** | feedmob-brand-guidelines | Create branded FeedMob PowerPoint presentations with automatic brand compliance |
| **gemini-image-generator** | feedmob-presentations | Generate custom images and insert them into presentation slides |
| **civitai-analyst** | feedmob-presentations | Create visual reports from Civitai analytics data |
| **ai-news-daily** | feedmob-presentations | Generate AI industry briefing presentations |
| **url-parameter-parser** | civitai-analyst | Process CSV data before database analysis |

## Quick Start Examples

### Example 1: Create a Branded FeedMob Presentation

```bash
# Automatically uses feedmob-brand-guidelines for compliance
# and feedmob-presentations for generation

"Create a FeedMob presentation about Q1 analytics results 
with title slide, 3 content slides, and a metrics dashboard"
```

### Example 2: Analyze Civitai Video Performance

```bash
# Uses civitai-analyst skill

"Show me the top 10 performing videos this week with 
engagement metrics and tag analysis"

# Or in Chinese:
"生成本周的视频表现周报"
```

### Example 3: Generate Marketing Images

```bash
# Uses gemini-image-generator skill

"Generate a 16:9 hero image for our landing page featuring 
a modern office with people using mobile devices. 
Give me 3 variations in 2K resolution."
```

### Example 4: Daily AI News Briefing

```bash
# Uses ai-news-daily skill

"Give me today's top AI news stories focusing on 
LLMs and computer vision developments"
```

### Example 5: Process URL Data

```bash
# Uses url-parameter-parser skill

"Extract all query parameters from the URLs in 
campaign_data.csv and add them as new columns"
```

## Trigger Keywords Reference

Skills can be automatically activated when you mention certain keywords or phrases:

| Skill | Trigger Keywords/Phrases |
|-------|-------------------------|
| **feedmob-brand-guidelines** | FeedMob branding, brand guidelines, FeedMob colors, FeedMob logo, branded content |
| **feedmob-presentations** | PowerPoint, PPT, presentation, slides, create presentation |
| **civitai-analyst** | Civitai, video stats, engagement, likes, hearts, comments, weekly report, tag analysis, 数据分析, 视频表现, 周报 |
| **url-parameter-parser** | URL parameters, parse URLs, CSV, extract parameters, query string |
| **gemini-image-generator** | generate image, edit image, Gemini, image generation, aspect ratio, logo overlay |
| **ai-news-daily** | AI news, latest AI, AI research, AI trends, AI developments, daily briefing |

## Project Structure

```
agent-skills/
├── .claude-plugin/          # Claude Code plugin configuration
├── skills/                  # 6 skill implementations
│   ├── ai-news-daily/
│   ├── civitai-analyst/
│   ├── feedmob-brand-guidelines/
│   ├── feedmob-presentations/
│   ├── gemini-image-generator/
│   └── url-parameter-parser/
├── spec/                    # Agent Skills specification
├── template/                # Skill template for creating new skills
└── README.md
```

## Creating a Skill

Skills are simple to create—just a folder with a `SKILL.md` file containing YAML frontmatter and instructions:

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name

[Add your instructions here that Claude will follow when this skill is active]

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

### Required Frontmatter Fields
- `name` - Unique identifier (lowercase, hyphens for spaces)
- `description` - Complete description of skill purpose and use cases

## Using Skills

### Claude Code
You can register this repository as a Claude Code Plugin marketplace by running the following command in Claude Code:
```
/plugin marketplace add feed-mob/agent-skills
```

Then, to install a specific set of skills:
1. Select `Browse and install plugins`
2. Select `feedmob-agent-skills`
3. Select `feedmob-content-tools` or `data-processing-tools`
4. Select `Install now`

Alternatively, directly install either Plugin via:
```
/plugin install feedmob-content-tools@feedmob-agent-skills
/plugin install data-processing-tools@feedmob-agent-skills
```

After installing the plugin, you can use the skill by just mentioning it.

### Claude.ai
To use any skill from this repository or upload custom skills, follow the instructions in [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude#h_a4222fa77b).

### Claude API
Use pre-built or custom skills via the API. See the [Skills API documentation](https://docs.claude.com/en/api/skills-guide#creating-a-skill).

## Getting Started

1. Browse the `skills/` directory for examples
2. Use the `template/` directory as a starting point for new skills
3. Follow the `spec/` for detailed guidelines
