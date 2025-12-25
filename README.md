# Agent Skills

A collection of skills for Claude agents to perform specialized tasks.

## What Are Skills?

**Skills** are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. They teach Claude how to complete specific tasks in a repeatable way.

## Project Structure

```
agent-skills/
├── .claude-plugin/          # Claude Code plugin configuration
├── skills/                  # Skill implementations
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
Register the repository as a marketplace plugin and install skills.

### Claude.ai
Upload custom skills via the web interface (available to paid plans).

### Claude API
Use pre-built or custom skills via the API. See the [Skills API documentation](https://docs.claude.com/en/api/skills-guide#creating-a-skill).

## Getting Started

1. Browse the `skills/` directory for examples
2. Use the `template/` directory as a starting point for new skills
3. Follow the `spec/` for detailed guidelines
