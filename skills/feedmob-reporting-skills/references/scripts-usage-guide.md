# Scripts Usage Guide

This guide details how to use automation scripts to calculate Gross Spend comparisons and generate multi-dimensional analysis reports.

## Overview

**Recommended Workflow (must execute in order):**
1. Use MCP tools to fetch data and download CSV (Steps 1-2)
2. Use `calculate_gross_spend_datafusion.py` to calculate comparison (Step 3.5)
3. **🚨 Mandatory: Use `analyze_gross_spend_datafusion.py` to generate summary data (Step 3.6)**
4. LLM reads summary CSVs and generates final report (Step 4)

---

## Step 3.5: Calculate Gross Spend Comparison

### Available Script Versions

| Script | Speed | Dependencies | Recommended Scenario |
|--------|-------|--------------|---------------------|
| **DataFusion Python** ⭐⭐ | ~0.1s | Auto-install | **Most Recommended** |
| Standard Library Python | ~0.5s | No install needed | Backup/zero-dependency |

### DataFusion Python Version (Recommended)

**First use Glob to find:** `**/calculate_gross_spend_datafusion.py`

```bash
python3 scripts/calculate_gross_spend_datafusion.py \
    <attribution_report.csv> \
    <histories.csv> \
    <direct_spend.csv> \
    <output.csv>
```

**Features:**
- ✅ Universal support for all clients
- ✅ Auto-installs dependencies (datafusion, pandas, pyarrow)
- ✅ Uses correct formula: `client_paid_action_count × gross_cpi`
- ✅ Dynamically matches event fields
- ✅ Automatically filters zero-activity rows

### Standard Library Python Version (Backup)

**First use Glob to find:** `**/calculate_gross_spend.py`

```bash
python3 scripts/calculate_gross_spend.py \
    --report <report.csv> \
    --histories <histories.csv> \
    --direct-spend <spend.csv> \
    --output <output.csv>
```

---

## Step 3.6: Generate Multi-Dimensional Analysis Summary (⚠️ Mandatory)

### Why is this a mandatory step?

When comparison reports contain large amounts of data, LLM directly reading will cause:
- ❌ Extremely high hallucination risk
- ❌ Token limit exceeded
- ❌ Calculation errors

**✅ Correct approach: Let DataFusion SQL process data first**

### Use Script

**First use Glob to find:** `**/analyze_gross_spend_datafusion.py`

```bash
python3 scripts/analyze_gross_spend_datafusion.py \
    <comparison_report.csv> \
    <output_directory>
```

### Generated 10 Analysis Dimensions

| File | Content | Purpose |
|------|---------|---------|
| `01_global_summary.csv` | Global summary statistics | Quick overview |
| `02_by_vendor.csv` | Grouped by Vendor | Identify problem vendors |
| `03_by_paid_action.csv` | Grouped by Paid Action | Analyze by event type |
| `04_cpm_vs_cpi.csv` | CPM vs CPI comparison | Distinguish billing models |
| `05_match_status.csv` | Match status analysis | View match rate |
| `06_top50_anomalies.csv` | Top 50 largest differences | Focus on issues |
| `07_by_click_url.csv` | Summarized by Click URL | Campaign-level analysis |
| `08_daily_trend.csv` | Daily trend | Time series analysis |
| `09_duplicates.csv` | Duplicate record detection | Data quality check |
| `10_weekly_trend.csv` | Weekly summary | Week-level trends |

**Total Token Usage: ~8,800** (well below 25,000 limit)

### LLM Analysis Workflow

**Prerequisites (must complete):**
1. Already ran `analyze_gross_spend_datafusion.py`
2. Confirmed 10 summary CSV files were generated

**Reading Order:**
1. Read global summary (1 row)
2. Read key groupings (~20 rows)
3. Read Top anomalies (if there are differences)
4. Read trend data
5. Generate business report

---

## Related Documentation

- [Calculation Verification Guide](calculation-verification-guide.md) - Calculation rules
- [Anti-Hallucination Protocol](anti-hallucination-protocol.md) - Anti-hallucination rules
- [Report Structure Guide](report-structure.md) - Report structure
