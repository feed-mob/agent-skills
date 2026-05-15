---
name: feedmob-reporting-skills
description: "MUST use this skill when using mcp__feedmob-reporting__* tools. Provides structured workflows for FeedMob reporting analysis. Key: All clients (Possible Finance, Koho Financial, TextNow, AppsFlyer MMP, etc.) use client_paid_action_count × gross_cpi (dynamic event field based on client_paid_action in click_url_histories). Critical for ensuring correct multi-step workflows and accurate data reconciliation. Trigger words: any feedmob-reporting MCP tool usage, Possible Finance, Koho Financial, TextNow, AppsFlyer, Singular reports, Adjust reports, direct spend, gross spend verification, spend reconciliation, client_paid_action."
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

This skill provides structured workflows for FeedMob reporting tasks using feedmob-reporting MCP tools. Includes processes for Possible Finance, Koho Financial spend verification, TextNow Adjust report analysis, AppsFlyer MMP clients, and cross-platform spend reconciliation.

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
| `compare_client_report_spend_datafusion.py` | **All clients** | ~0.1s | **Client report vs direct spend comparison** |
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
- ✅ Koho Financial (Singular reports)
- ✅ TextNow (Adjust reports)
- ✅ Privacy Hawk (Singularreports)
- ✅ Uber Technologies (AgencyConversionRecords)
- ✅ AppsFlyer MMP clients (universal AppsFlyer reports)
- ✅ Any future clients

**When to use:** When verifying spend accuracy, reconciling reports, or investigating spend mismatches.

**Workflow Steps:**

#### Step 1: Fetch Attribution Report

**Choose tool based on client:**
- Possible Finance → `get_possible_finance_singular_reports`
- Koho Financial → `get_koho_financial_singular_reports`
- TextNow → `get_textnow_adjust_reports`
- Privacy Hawk → `get_privacy_hawk_singular_reports`
- Uber Technologies → See [Uber Workflow](references/uber-workflow.md)
- AppsFlyer MMP clients → See [AppsFlyer Workflow](references/appsflyer-mmp-workflow.md)

**For detailed API calls, data validation, and CSV saving process, see:**
**[Data Collection Guide](references/data-collection-guide.md)**

#### Step 1.5: Fetch Partner Reports (When vendor_managed Campaigns Exist)

**When to use:** When `click_url_histories` contains entries with `client_paid_action = "vendor_managed"` and `margin` field.

**Why needed:** Vendor-managed campaigns (CPM billing) don't have event data in attribution reports. Instead, gross spend is calculated from partner `partner_net_spend` and `margin`:
```
calculated_gross = partner_net_spend × (1 - margin/100)
```

**Choose tool based on partner:**
- Jampp → `get_jampp_reports` (requires `client_id`)
- Kayzen → `get_kayzen_reports`
- YouAppi → `get_youappi_reports`
- Samsung → `get_samsung_reports`

**Example:**
```javascript
// Fetch Jampp partner report (if Jampp vendor_managed campaigns exist)
mcp__feedmob-reporting__get_jampp_reports({
  client_id: 123,
  start_date: "2026-01-15",
  end_date: "2026-01-15"
})
```

**Save the response CSV** for use in Step 3.5.

---

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
    <attribution_report.csv> <histories.csv> <direct_spend.csv> <output.csv> \
    [partner_report1.csv partner_report2.csv ...]
```

**Optional partner_report CSVs:** When vendor_managed campaigns exist, pass one or more partner report CSVs as additional arguments. The script will:
1. Run the standard query for non-vendor_managed campaigns
2. Run a vendor_managed query calculating `partner_net_spend × (1 - margin/100)`
3. Merge both results into a single output CSV

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

### 2. Net Spend Verification Workflow (Partner Reports)

Compare partner reports (Jampp, Kayzen, etc.) with direct spend data to verify net spend accuracy.

**Applicable Partners:**
- ✅ Jampp
- ✅ Kayzen
- ✅ YouAppi
- ✅ Samsung
- ✅ Smadex
- ✅ InMobi
- ✅ Liftoff

**When to use:** When verifying net spend from partner platforms against FeedMob direct spend records.

**Key Difference from Gross Spend:**
- **Gross Spend**: Requires calculation (`client_paid_action_count × gross_cpi`)
- **Net Spend**: Direct comparison (`partner_net_spend` vs `feedmob_net_spend`)

**Workflow Steps:**

#### Step 1: Fetch Partner Report

**Direct Partners (Jampp, Kayzen, YouAppi, Samsung):**

```javascript
// Jampp - requires client_id
mcp__feedmob-reporting__get_jampp_reports({
  client_id: 123,
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})

// Kayzen - no client_id required
mcp__feedmob-reporting__get_kayzen_reports({
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})

// YouAppi - no client_id required
mcp__feedmob-reporting__get_youappi_reports({
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})

// Samsung - no client_id required
mcp__feedmob-reporting__get_samsung_reports({
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})
```

**Multi-step Partners (Smadex, InMobi, Liftoff):**

**Smadex (3-step process):**
```javascript
// Step 1: Get report IDs
mcp__feedmob-reporting__get_smadex_report_ids({
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})

// Step 2: Check status (repeat until ready)
mcp__feedmob-reporting__check_smadex_report_status({
  report_id: "abc-123"
})

// Step 3: Get report data when status is "ready"
mcp__feedmob-reporting__get_smadex_reports({
  report_id: "abc-123"
})
```

**InMobi (3-step process):**
```javascript
// Step 1: Get report IDs
mcp__feedmob-reporting__get_inmobi_report_ids({
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})

// Step 2: Check status (repeat until ready)
mcp__feedmob-reporting__check_inmobi_report_status({
  report_id: "abc-123",
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})

// Step 3: Get report data when status is "ready"
mcp__feedmob-reporting__get_inmobi_reports({
  skan_report_id: "skan-123",
  non_skan_report_id: "non-skan-456",
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})
```

**Liftoff (3-step process):**
```javascript
// Step 1: Get report IDs
mcp__feedmob-reporting__get_liftoff_report_ids({
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})

// Step 2: Check status (repeat until ready)
mcp__feedmob-reporting__check_liftoff_report_status({
  stash_report_id: "stash-123",
  possible_finance_report_id: "pf-456"
})

// Step 3: Get report data when status is "ready"
mcp__feedmob-reporting__get_liftoff_reports({
  stash_report_id: "stash-123",
  possible_finance_report_id: "pf-456",
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})
```

**Response contains:**
- `click_url_id`: Click URL identifier
- `partner_net_spend`: Net spend from partner report
- `date`: Report date
- Other partner-specific fields

#### Step 2: Extract Click URL IDs and Fetch Direct Spends

From partner report, extract all unique `click_url_id` values, then fetch direct spends:

```javascript
mcp__feedmob-reporting__get_direct_spends({
  start_date: "2025-01-01",
  end_date: "2025-01-31",
  click_url_ids: ["12345", "12346", ...]  // string array
})
```

#### Step 3: Use Automation Scripts (Recommended)

**Step 3.1: Compare Net Spend**

First use Glob to find: `**/compare_net_spend_datafusion.py`

```bash
python3 scripts/compare_net_spend_datafusion.py \
    <partner_report.csv> <direct_spend.csv> <output.csv>
```

**Step 3.2: Generate Analysis Summary**

```bash
python3 scripts/analyze_net_spend_datafusion.py \
    <comparison_report.csv> <output_directory>
```

**For detailed script usage, see:**
**[Scripts Usage Guide](references/scripts-usage-guide.md)**

#### Step 4: Generate Final Report

Compare `partner_net_spend` vs `feedmob_net_spend`:

| Click URL | Date | Partner Net | FeedMob Net | Difference | Diff % | Status |
|-----------|------|-------------|-------------|------------|--------|--------|
| 12345 | 2025-01-01 | $1,500.00 | $1,500.00 | $0.00 | 0.00% | ✅ |
| 12346 | 2025-01-01 | $2,000.00 | $1,950.00 | $50.00 | 2.56% | 🚨 |

**Status Icons:**
- ✅ **Perfect Match**: 0% difference
- ⚠️ **Minor Difference**: <2% difference
- 🚨 **Significant Difference**: ≥2% difference

**For detailed report structure, see:**
**[Report Structure Guide](references/report-structure.md)**

---

### 3. AppsFlyer MMP Client Workflow

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

### 4. Client Report Spend Comparison Workflow

Compare client-provided `gross_spend` against `feedmob_gross_spend` directly — no event calculation needed.

**Steps:**
1. Fetch client report: `get_client_report_spend_report_names()` → `get_client_report_spends()`
2. Fetch direct spends: `get_direct_spends()`
3. Run: `python3 scripts/compare_client_report_spend_datafusion.py <client_report.csv> <direct_spend.csv> <output.csv>`

**For detailed script usage, comparison modes, and output format, see:**
**[Client Report Comparison Guide](references/client-report-comparison-guide.md)**

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
- **[Client Report Comparison Guide](references/client-report-comparison-guide.md)** - Client report vs direct spend comparison
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

