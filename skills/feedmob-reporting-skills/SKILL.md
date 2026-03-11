---
name: feedmob-reporting-skills
description: "MUST use this skill when using mcp__feedmob-reporting__* tools. Provides structured workflows for FeedMob reporting analysis. Key: All clients (Possible Finance, TextNow, AppsFlyer MMP, etc.) use client_paid_action_count × gross_cpi (dynamic event field based on client_paid_action in click_url_histories). Critical for ensuring correct multi-step workflows and accurate data reconciliation. Trigger words: any feedmob-reporting MCP tool usage, Possible Finance, TextNow, AppsFlyer, Singular reports, Adjust reports, direct spend, gross spend verification, spend reconciliation, client_paid_action."
---

# FeedMob Reporting Skills

## 🚨🚨🚨 STOP AND READ THIS FIRST 🚨🚨🚨

**Critical Principle: Prevent Hallucinated Numbers**

Before performing any spend verification analysis, you MUST follow the anti-hallucination protocol. For detailed rules, see:
**[Anti-Hallucination Protocol](references/anti-hallucination-protocol.md)**

**Core Rules Summary:**
- ❌ NEVER make up, guess, or calculate numbers in your head
- ✅ MUST display raw data → aggregation table → calculation steps → final report
- ✅ All numbers must be traceable to tool responses
- ✅ Use correct formula: `client_paid_action_count × gross_cpi`
- ✅ Dynamically check `client_paid_action`, don't hard-code event fields

**Mandatory Workflow:**
1. Display raw data rows (from tool responses)
2. Create aggregation table (grouped by date, click_url_id)
3. Display calculation steps (each multiplication)
4. Spot-check 3 data points to verify accuracy
5. Then and only then generate final report

Complete anti-hallucination rules, verification checklist, and examples in [references/anti-hallucination-protocol.md](references/anti-hallucination-protocol.md)

---

## Overview

This skill provides structured workflows for FeedMob reporting tasks using feedmob-reporting MCP tools. Includes processes for Possible Finance spend verification, TextNow Adjust report analysis, AppsFlyer MMP clients, and cross-platform spend reconciliation.

## Important: MCP Tool Usage

**First check if MCP tools are available:**
- If `mcp__feedmob-reporting__*` tools are available, call them directly
- If tools are unavailable (call fails or doesn't exist), ask user to configure MCP server

**When tools are available:**
- ✅ Call `mcp__feedmob-reporting__get_possible_finance_singular_reports(...)` directly
- ✅ No need to check configuration or installation

**When tools are unavailable:**
- ✅ Inform user they need to configure feedmob-reporting MCP server
- ✅ Provide configuration instructions or guide user to MCP server documentation

## 🚀 Quick Start: Automation Scripts (Recommended)

Before diving into detailed workflows, understanding available automation scripts can greatly simplify your work.

### Available Scripts Overview

| Script | Supported Clients | Speed | Recommended Scenario |
|--------|------------------|-------|---------------------|
| `calculate_gross_spend_datafusion.py` ⭐⭐ | **All clients** | ~0.1s | **Calculate comparison (Step 3.5, recommended)** |
| `analyze_gross_spend_datafusion.py` ⭐⭐ | **All clients** | ~0.1s | **Generate summary (Step 3.6, mandatory)** |
| `calculate_gross_spend.py` | **All clients** | ~0.5s | Backup/zero-dependency environment |

**Important Notes:**
- ✅ **All scripts are now universal**, supporting any client (Possible Finance, TextNow, etc.)
- ✅ Automatically adapt to different report structures (Singular, Adjust, etc.)
- ✅ Dynamic CSV column detection, no code modification needed for new clients
- 📖 Detailed script usage instructions in "Step 3.5" section of each workflow

**Recommended Workflow (must execute in order):**
1. Use MCP tools to fetch data and download CSV (Steps 1-2)
2. Use `calculate_gross_spend_datafusion.py` to calculate comparison (Step 3.5)
3. **🚨 Mandatory: Use `analyze_gross_spend_datafusion.py` to generate summary data (Step 3.6)**
4. LLM reads summary CSV and generates final report (Step 4)

**⚠️ Warning: Don't skip Step 3.6!**
- Summary data generated in Step 3.6 is the foundation for LLM to generate accurate reports
- Skipping this step leads to LLM manual calculation → extremely high hallucination risk
- All numbers must come from DataFusion summary, not LLM memory or manual calculation

---

## Core Workflows

### 1. Gross Spend Verification Workflow (Universal)

Compare attribution reports (Singular/Adjust/etc.) with direct spend data to identify discrepancies.

**Applicable Clients:**
- ✅ Possible Finance (Singular reports)
- ✅ TextNow (Adjust reports)
- ✅ Privacy Hawk (Singular reports)
- ✅ Uber Technologies (Agency Conversion Records)
- ✅ AppsFlyer MMP clients (universal AppsFlyer reports)
- ✅ Any future clients

**When to use:** When verifying spend accuracy, reconciling reports, or investigating spend mismatches.

**Workflow Steps:**

#### Step 1: Fetch Attribution Report

**Choose tool based on client:**
- Possible Finance → `get_possible_finance_singular_reports`
- TextNow → `get_textnow_adjust_reports`
- Privacy Hawk → `get_privacy_hawk_singular_reports`
- Uber Technologies → See [Uber Workflow](references/uber-workflow.md)
- AppsFlyer MMP clients → See [AppsFlyer Workflow](references/appsflyer-mmp-workflow.md)

**For detailed API calls, data validation, and CSV saving process, see:**
**[Data Collection Guide](references/data-collection-guide.md)**

#### Step 2: Fetch Historical Rates and Direct Spend (Parallel)

**Call two tools in parallel:**
- `get_click_url_histories` - number array `[12345, 12346]`
- `get_direct_spends` - string array `["12345", "12346"]`

**For detailed type differences, CSV saving, and parallel download process, see:**
**[Data Collection Guide](references/data-collection-guide.md)**

#### Step 3: Match Event Fields and Calculate Expected Gross Spend

**🚨 Mandatory: Use Correct Formula**
```
calculated_gross_spend = client_paid_action_count × gross_cpi
```

**Key Requirements:**
- ✅ Dynamically match `client_paid_action` field (don't hard-code)
- ✅ Aggregate multiple rows for same click_url_id
- ✅ Use `gross_cpi` (not `gross_rate`)
- ✅ MUST display verification sections before calculating (raw data, aggregation, calculation steps)

**For detailed calculation rules, verification requirements, and examples, see:**
**[Calculation Verification Guide](references/calculation-verification-guide.md)**

**Quick Checklist:**
- [ ] Aggregated multiple rows for same click_url_id?
- [ ] Used correct event field?
- [ ] Used gross_cpi instead of gross_rate?
- [ ] Displayed verification sections (A, B, C)?

#### Step 3.5: Use Automation Scripts (Recommended)

**DataFusion Python Version (auto-installs dependencies):**

First use Glob to find: `**/calculate_gross_spend_datafusion.py`

```bash
python3 scripts/calculate_gross_spend_datafusion.py \
    <attribution_report.csv> <histories.csv> <direct_spend.csv> <output.csv>
```

**For detailed script version comparison, parameter descriptions, and usage examples, see:**
**[Scripts Usage Guide](references/scripts-usage-guide.md)**

#### Step 3.6: Generate Multi-Dimensional Analysis Summary (⚠️ Mandatory)

**🚨 Important: This is a mandatory step, cannot be skipped!**

**Why mandatory?**
- Prevents LLM hallucinations and calculation errors
- Avoids token limit exceeded
- Lets SQL engine handle data aggregation

```bash
python3 scripts/analyze_gross_spend_datafusion.py \
    <comparison_report.csv> \
    <output_directory>
```

**Generates 10 summary dimensions:** Global, Vendor, Click URL, trends, etc.

**LLM reading order:**
1. Read global summary
2. Read key groupings (Vendor, Paid Action)
3. Read Top anomalies
4. Generate business report

**For detailed script descriptions, 10 analysis dimensions, and LLM workflow, see:**
**[Scripts Usage Guide](references/scripts-usage-guide.md)**

---

#### Step 4: Generate Final Report

**Prerequisites:** Completed Steps 3.5 and 3.6, read summary CSVs

**🚨 MUST reference standard format and section order defined in [Report Structure Guide](references/report-structure.md).**

**🎯 Report Structure**

For detailed report structure and formatting guide, see: **[Report Structure Guide](references/report-structure.md)**

**Core Principles:**
- Separate CPM and Non-CPM activities
- Non-CPM: Show Click URL and Vendor level comparison
- CPM: Only show Direct Spend (cannot verify without CPM rates)
- Only include Non-CPM accuracy statistics
- Sort tables by Calculated Gross (descending)
- Use status icons: ✅ (0-1%), ⚠️ (1-2%), 🚨 (≥2%)

**Standard Sections:**
1. Overall Summary
2. Non-CPM Activity Comparison (Click URL + Vendor tables)
3. CPM Activity Section (separate)
4. Verification Accuracy Statistics
5. Key Findings and Recommendations

---

### 2. AppsFlyer MMP Client Workflow

Use this workflow when client uses AppsFlyer as MMP (instead of Singular or Adjust).

**Key Features:**
- ✅ First call `get_clients` to check client's `mmp_track_party` field
- ✅ Use `get_appsflyer_reports` to fetch attribution report
- ✅ Subsequent steps identical to other clients (Possible Finance, TextNow)
- ✅ Supports multiple clients, various filter options (client_ids, af_app_ids, campaign_ids)

**For detailed workflow, examples, and considerations, see:**
**[AppsFlyer MMP Client Workflow Guide](references/appsflyer-mmp-workflow.md)**

**Quick Start:**
1. Check client MMP type: `get_clients({ client_name: "..." })`
2. Fetch AppsFlyer reports: `get_appsflyer_reports({ client_ids: [...] })`
3. Fetch historical rates and direct spend (parallel)
4. Use DataFusion scripts to calculate comparison and generate summary
5. Read summary CSVs and generate report

---

## Reference Documentation

The following reference documents provide detailed workflow guides, best practices, and troubleshooting solutions:

### Core Guides
- **[Anti-Hallucination Protocol](references/anti-hallucination-protocol.md)** - Mandatory rules for ensuring number accuracy
- **[Data Collection Guide](references/data-collection-guide.md)** - API calls, data validation, and CSV saving
- **[Calculation Verification Guide](references/calculation-verification-guide.md)** - Event matching and Gross Spend calculation rules
- **[Scripts Usage Guide](references/scripts-usage-guide.md)** - Automation scripts and multi-dimensional analysis
- **[Report Structure Guide](references/report-structure.md)** - Standardized report format and best practices

### Workflow Guides
- **[Uber Technologies Workflow](references/uber-workflow.md)** - Handling Uber Technologies using agency conversion records
- **[AppsFlyer MMP Client Workflow](references/appsflyer-mmp-workflow.md)** - Handling clients using AppsFlyer MMP

### Tools and Troubleshooting
- **[MCP Tools Reference](references/mcp_tools.md)** - Detailed descriptions of all available MCP tools
- **[Troubleshooting Guide](references/troubleshooting.md)** - Common issue solutions

**Quick Find Common Issues:**
- Missing click_url_ids or empty results → [Troubleshooting](references/troubleshooting.md)
- Type conversion errors → [Troubleshooting](references/troubleshooting.md)
- CPM campaigns handling → [Troubleshooting](references/troubleshooting.md)
- Inaccurate numbers or hallucinations → [Anti-Hallucination Protocol](references/anti-hallucination-protocol.md)
- Uber Technologies workflow → [Uber Workflow](references/uber-workflow.md)
- AppsFlyer client workflow → [AppsFlyer MMP Workflow](references/appsflyer-mmp-workflow.md)

---

