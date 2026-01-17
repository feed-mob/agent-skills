# FeedMob Reporting Skills

## Overview

Structured workflows and best practices for FeedMob reporting analysis using feedmob-reporting MCP tools.

## ⚠️ Important Usage Note

**ALWAYS load this skill before using any `mcp__feedmob-reporting__*` tools:**

When you see or need to use tools like:
- `mcp__feedmob-reporting__get_possible_finance_singular_reports`
- `mcp__feedmob-reporting__get_direct_spends`
- Any other `mcp__feedmob-reporting__*` tool

First use the Skill tool to load this skill:
```
Skill(skill: "feedmob-reporting-skills")
```

This ensures you follow the correct workflows and best practices.

## What This Skill Provides

### 1. Structured Workflows
- **Possible Finance Gross Spend Check** - Optimized 3-step workflow with parallel tool execution
- **InMobi Report Analysis** - Proper sequence for fetching and validating InMobi data with status checks
- **AppsFlyer Report Verification** - Cross-reference methodology with direct spend comparison
- **Agency Conversion Metrics** - Performance analysis and rejection rate investigation

### 2. Execution Principles
- **Immediate execution** - Start with tool calls, no planning phase
- **Parallel tool calls** - Maximize efficiency by calling independent tools together
- **Data type awareness** - Correct parameter types (number[] vs string[])
- **Error handling** - Graceful handling of empty responses and missing data

### 3. Best Practices
- Date format standards (YYYY-MM-DD)
- Error handling patterns
- Data validation techniques
- Calculation formulas

### 4. Common Calculations

**Possible Finance:**
```
gross_spend = client_paid_action_count × gross_cpi
net_spend = client_paid_action_count × net_cpi
```

Note: `client_paid_action` (e.g., "tutorial", "registration", "install") from click_url_histories determines which event count to use from Singular reports.

**TextNow:**
```
gross_spend = client_paid_action_count × gross_cpi
net_spend = client_paid_action_count × net_cpi
```

**Discrepancy:**
```
discrepancy_% = ((calculated - actual) / calculated) × 100
```

## Quick Examples

### Check Possible Finance Spend
```
User: "Check Possible Finance gross spend for 2026-01-01"
Assistant: [Immediately calls get_possible_finance_singular_reports]
Assistant: [After response, calls get_click_url_histories AND get_direct_spends in parallel]
Assistant: [Calculates and presents comparison report]
```

### Analyze InMobi Reports
```
User: "Get InMobi reports for last week"
Assistant: [Loads feedmob-reporting-skills skill]
Assistant: [Follows InMobi workflow: get IDs → check status → fetch reports → compare]
```

## Why Use This Skill?

Without this skill, you might:
- ❌ Skip critical steps (like fetching historical gross rates)
- ❌ Use wrong calculation formulas
- ❌ Present data in inconsistent formats
- ❌ Miss important validation checks
- ❌ Search for MCP configuration unnecessarily
- ❌ Call tools sequentially instead of in parallel

With this skill, you will:
- ✅ Follow proven, optimized workflows
- ✅ Use correct calculations
- ✅ Present clear, tabular reports
- ✅ Catch data discrepancies
- ✅ Execute tools immediately and efficiently
- ✅ Maximize performance with parallel tool calls

## Available MCP Tools

This skill guides the usage of these tools:
- `get_possible_finance_singular_reports`
- `get_inmobi_report_ids`
- `check_inmobi_report_status`
- `get_inmobi_reports`
- `get_appsflyer_reports`
- `get_direct_spends`
- `get_agency_conversion_records`
- `get_click_url_histories`
- `create_direct_spend`
- `get_adops_reports`
- `get_clients`
- `get_campaigns`
- `get_vendors`

## Reference Files

- `SKILL.md` - Complete workflows and procedures
- `references/mcp_tools.md` - Detailed tool documentation
- `references/workflow_examples.md` - Real-world usage examples

## Support

For issues or questions about this skill, refer to the workflow examples in `references/workflow_examples.md`.
