# Agent Skills Specification

This directory contains the specification and guidelines for creating agent skills.

## Overview

Agent Skills are structured instructions that teach Claude how to perform specialized tasks. This specification defines:

- Skill structure and format requirements
- YAML frontmatter schema
- Best practices for skill development
- Integration guidelines

## Skill Structure

Every skill must include:

1. **SKILL.md** - Main skill file with:
   - YAML frontmatter (name, description)
   - Instructions for Claude
   - Examples and guidelines

2. **Optional files**:
   - README.md - Developer documentation
   - Scripts, configs, or data files
   - Assets and examples

## Frontmatter Schema

```yaml
---
name: string          # Required: unique identifier (lowercase-with-hyphens)
description: string   # Required: complete description of purpose and usage
version: string       # Optional: semantic version (e.g., "1.0.0")
author: string        # Optional: author or organization
tags: array           # Optional: categorization tags
---
```

## Best Practices

1. **Clear naming**: Use descriptive, action-oriented names
2. **Complete descriptions**: Explain what, when, and why
3. **Concrete examples**: Show actual usage scenarios
4. **Specific guidelines**: Provide actionable instructions
5. **Test thoroughly**: Validate behavior across use cases

## Integration

Skills can be used via:
- Claude Code CLI
- Claude.ai web interface
- Claude API

See main README.md for integration details.
