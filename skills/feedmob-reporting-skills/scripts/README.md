# FeedMob Reporting Scripts

This directory contains automation scripts for FeedMob reporting analysis.

## Script List

### 1. download_s3_csv.py

Download CSV data files from S3 URLs.

**Purpose:**
- Download Singular reports, click_url_histories, direct_spends, and other data
- Automatically extract ZIP files and extract CSV
- Support extracting s3_url from JSON responses

**Usage Examples:**
```bash
# Direct S3 URL
python3 download_s3_csv.py "https://s3.amazonaws.com/.../report.zip" --output-dir ./tmp

# Extract URL from JSON response
python3 download_s3_csv.py --from-json '{"data": {"s3_url": "https://..."}}' --output-dir ./tmp
```

**Parameters:**
- `url`: S3 URL (positional argument)
- `--from-json`: Extract s3_url from JSON string
- `--output-dir`: Output directory (default: current directory)
- `--keep-zip`: Keep ZIP file (default: delete)

---

### 2. calculate_gross_spend.py (Universal Version)

Calculate expected gross spend and compare with direct spend. **Works for all clients** (Possible Finance, TextNow, etc.).

**Version Selection:**
- **DataFusion Python Version** (`calculate_gross_spend_datafusion.py`) ⭐⭐: **Most recommended**, auto-installs dependencies, fastest execution (~0.1s)
- **Standard Version** (`calculate_gross_spend.py`): Zero dependencies, uses Python standard library, backup solution

**Features:**
- ✅ **Universal support**: Possible Finance (Singular), TextNow (Adjust), any future clients
- ✅ Uses formula: `client_paid_action_count × gross_cpi`
- ✅ Dynamically matches event fields (based on `client_paid_action`)
- ✅ Automatically aggregates multi-row data
- ✅ Filters zero-activity records
- ✅ Generates detailed comparison reports and statistics

**Usage Example (DataFusion Python Version - Recommended):** ⭐⭐
```bash
# No manual dependency installation needed, auto-installs on first run

# Possible Finance Example (fastest and most convenient)
python3 calculate_gross_spend_datafusion.py \
    ./tmp/possible_finance_singular_reports_2026-01-01_2026-01-20.csv \
    ./tmp/click_url_histories_2026-01-01_2026-01-20.csv \
    ./tmp/direct_spends_2026-01-01_2026-01-20.csv \
    ./tmp/gross_spend_comparison_report.csv

# TextNow Example
python3 calculate_gross_spend_datafusion.py \
    ./tmp/textnow_adjust_reports_2026-01-01_2026-01-20.csv \
    ./tmp/click_url_histories_2026-01-01_2026-01-20.csv \
    ./tmp/direct_spends_2026-01-01_2026-01-20.csv \
    ./tmp/gross_spend_comparison_report.csv
```

**DataFusion Python Version Features:** ⭐⭐
- ✅ **Auto-installs dependencies** (first run, no manual steps)
- ✅ **Universal support for all clients** (auto-adapts to any report structure)
- ✅ Fastest execution speed (~0.1s)
- ✅ Dynamic column detection, auto-adapts to CSV structure
- ✅ Cross-platform compatible (macOS, Linux, Windows)
- ✅ Uses requirements.txt for dependency version management
- ✅ English interface, easy to understand

**Usage Example (Standard Version - Zero Dependency Environment):**
```bash
# Possible Finance (Singular reports)
python3 calculate_gross_spend.py \
    --report ./tmp/possible_finance_singular_reports_2026-01-01_2026-01-20.csv \
    --histories ./tmp/click_url_histories_2026-01-01_2026-01-20.csv \
    --direct-spend ./tmp/direct_spends_2026-01-01_2026-01-20.csv \
    --output ./tmp/gross_spend_comparison_report.csv

# TextNow (Adjust reports)
python3 calculate_gross_spend.py \
    --report ./tmp/textnow_adjust_reports_2026-01-01_2026-01-20.csv \
    --histories ./tmp/click_url_histories_2026-01-01_2026-01-20.csv \
    --direct-spend ./tmp/direct_spends_2026-01-01_2026-01-20.csv \
    --output ./tmp/gross_spend_comparison_report.csv
```

**Parameters:**
- `--report`: Attribution report CSV file path (required)
- `--histories`: click_url_histories CSV file path (required)
- `--direct-spend`: direct_spends CSV file path (required)
- `--output`: Output report file path (default: `./tmp/gross_spend_comparison_report.csv`)
- `--show-zero`: Include zero-activity rows (default: filter out)

**Input CSV Formats:**

1. **Singular Report** (possible_finance_singular_reports_*.csv):
```
click_url_id,date,impression,click,install,registration,purchase
20743,2026-01-20,0,12046,134,310,17
```

2. **Click URL Histories** (click_url_histories_*.csv):
```
click_url_id,campaign_name,vendor_name,date,gross_cpi,net_cpi,client_paid_action,vendor_paid_action
19741,PossibleFinance_Android_US_CPI_Agency,Kayzen,2026-01-01,30.0,0.1,first_purchase,vendor_managed
```

3. **Direct Spends** (direct_spends_*.csv):
```
click_url_id,campaign_name,date,feedmob_net_spend,feedmob_gross_spend
19742,PossibleFinance_iOS_US_CPI_Agency,2026-01-01,307.81,308.0
```

**Output Report Format:**

CSV file contains the following fields:
```
date,click_url_id,campaign_name,vendor_name,
client_paid_action,event_field,event_count,gross_cpi,
calculated_gross_spend,direct_gross_spend,difference,difference_pct
```

**Terminal Output:**
```
============================================================
SUMMARY REPORT
============================================================

Total Calculated Gross Spend: $31,403.00
Total Direct Gross Spend:     $31,338.00
Total Difference:             $65.00 (0.21%)

Status: ✅ MATCH

============================================================
BREAKDOWN BY PAID ACTION
============================================================
  first_purchase: 1052 events, $31,403.00 calculated
```

**Status Indicators:**
- ✅ **MATCH**: Difference < 1%
- ⚠️ **MINOR DIFFERENCE**: 1% ≤ Difference < 5%
- 🚨 **SIGNIFICANT DIFFERENCE**: Difference ≥ 5%

---

## Complete Workflow Example

### Possible Finance Gross Spend Comparison

```bash
# Step 1: Download data files
python3 download_s3_csv.py "https://s3.amazonaws.com/.../possible_finance_singular_reports.zip" --output-dir ./tmp
python3 download_s3_csv.py "https://s3.amazonaws.com/.../click_url_histories.zip" --output-dir ./tmp
python3 download_s3_csv.py "https://s3.amazonaws.com/.../direct_spends.zip" --output-dir ./tmp

# Step 2: Calculate and compare
python3 calculate_gross_spend.py \
    --report ./tmp/possible_finance_singular_reports_2026-01-01_2026-01-20.csv \
    --histories ./tmp/click_url_histories_2026-01-01_2026-01-20.csv \
    --direct-spend ./tmp/direct_spends_2026-01-01_2026-01-20.csv \
    --output ./tmp/gross_spend_comparison_report.csv

# Step 3: View report
cat ./tmp/gross_spend_comparison_report.csv
```

---

## Version Selection Guide

### Performance Comparison

| Feature | Standard Library Version | **DataFusion Python** |
|---------|-------------------------|---------------------|
| **Dependencies** | Zero dependencies | Auto-install |
| **Execution Speed** | ~0.5s | **~0.1s** ✨ |
| **Auto-install Deps** | N/A | ✅ |
| **Dynamic Column Detection** | ✅ (runtime tolerance) | ✅ (pre-detection) |
| **Processing Method** | Row-by-row iteration + dict | Native SQL engine |
| **Memory Usage** | Load all into memory | Streaming |
| **Code Readability** | Medium | High (SQL) |
| **Cross-platform** | ✅ | ✅ |
| **Debugging Difficulty** | Easy | Easy |
| **Recommended Scenario** | Zero-dep env/backup | **Daily analysis** ✨✨ |

### Code Comparison Example

**Standard Library Version**:
```python
# Manually build mappings and loops
rate_map = {}
for row in histories_data:
    key = (int(row['click_url_id']), row['date'])
    rate_map[key] = {...}

results = []
for row in singular_data:
    key = (click_url_id, date)
    rate_info = rate_map.get(key)
    # ... calculation logic
    results.append({...})

# Manual merge
direct_spend_map = {}
for row in direct_spend_data:
    key = (int(row['click_url_id']), row['date'])
    direct_spend_map[key] = float(row['feedmob_gross_spend'])

merged_data = []
for row in calculated_data:
    key = (row['click_url_id'], row['date'])
    direct_gross = direct_spend_map.get(key, 0.0)
    # ... merge logic
```

**DataFusion Version**:
```sql
-- One SQL statement does everything
WITH calculated AS (
    SELECT
        s.date,
        s.click_url_id,
        h.campaign_name,
        CASE h.client_paid_action
            WHEN 'first_purchase' THEN s.purchase
            WHEN 'first_install' THEN s.install
        END as event_count,
        h.gross_cpi,
        event_count * h.gross_cpi as calculated_gross_spend
    FROM singular_report s
    INNER JOIN histories h
        ON s.click_url_id = h.click_url_id
        AND s.date = h.date
)
SELECT
    c.*,
    d.feedmob_gross_spend as direct_gross_spend,
    c.calculated_gross_spend - d.feedmob_gross_spend as difference
FROM calculated c
LEFT JOIN direct_spend d
    ON c.click_url_id = d.click_url_id
    AND c.date = d.date
```

### DataFusion Advantages

1. **SQL Expressiveness**: Complex JOINs and aggregations are clear at a glance
2. **Vectorized Execution**: Batch process data, leverage CPU cache
3. **Query Optimization**: Automatically optimize query plans
4. **Type Safety**: Automatic type inference and validation
5. **Scalability**: Supports efficient formats like Parquet, Arrow

### When to Choose Which Version

**Choose DataFusion Python Version (Highly Recommended):** ✨✨
- ✅ **Daily analysis and report generation** (first choice)
- ✅ **First-time users or new users** (auto-installs dependencies, no configuration needed)
- ✅ Any file size (fast for small to large files, ~0.1s)
- ✅ Need fastest execution speed (~5x faster than standard version)
- ✅ CSV structure may change (dynamic adaptation)
- ✅ Need auditable SQL queries
- ✅ Cross-platform compatible (macOS, Linux, Windows)

**Choose Standard Library Version:**
- ✅ **Zero-dependency environment** (completely unable to install external packages)
- ✅ Restricted environments (like Docker, CI/CD)
- ✅ As verification baseline
- ✅ Temporary use or quick verification
- ✅ Backup solution when DataFusion Python is unavailable

---

## Technical Details

### Calculation Formula

**Unified Formula for Possible Finance & TextNow:**
```
calculated_gross_spend = client_paid_action_count × gross_cpi
```

**Key Points:**
1. `client_paid_action` is retrieved from click_url_histories (dynamic field)
2. Event count field is mapped based on `client_paid_action`:
   - `first_purchase` → `purchase`
   - `first_install` → `install`
   - `registration` → `registration`
   - `impression` → `impression`
3. Rate uses `gross_cpi` (not `gross_rate`)

### Event Field Mapping

```python
event_field_map = {
    'first_purchase': 'purchase',
    'first_install': 'install',
    'registration': 'registration',
    'impression': 'impression',
    'click': 'click'
}
```

### Data Processing Flow

1. **Load Data**: Read three CSV files
2. **Build Rate Mapping**: `(click_url_id, date) → (gross_cpi, client_paid_action)`
3. **Calculate Gross Spend**:
   - Find corresponding event field based on `client_paid_action`
   - Get event count
   - Calculate: `count × gross_cpi`
4. **Merge Data**: Merge calculation results with direct spend
5. **Filter Zero Rows**: Remove records where both sides are 0
6. **Generate Report**: Output CSV and terminal statistics

---

## Troubleshooting

### Common Issues

**Q: Script error "No module named 'pandas'"**
A: This script doesn't depend on pandas, only uses Python standard library. If you see this error, check if you're running an old version.

**Q: There are discrepancies in the report, how to investigate?**
A:
1. Check the `difference` column to find discrepancy records
2. Verify event counts in attribution report
3. Confirm if corresponding records exist in direct_spends
4. Check rates and client_paid_action in click_url_histories

**Q: Zero-activity rows were filtered out, how to view them?**
A: Re-run the script with `--show-zero` parameter

**Q: How to verify calculations are correct?**
A: Manually spot-check a few records:
```bash
# Find a record in CSV
grep "2026-01-01,19742" ./tmp/gross_spend_comparison_report.csv

# Verify: event_count × gross_cpi = calculated_gross_spend
```

---

## Dependency Requirements

### Standard Version Scripts
- Python 3.6+
- Only uses standard library:
  - `csv`
  - `argparse`
  - `pathlib`
  - `collections`
  - `urllib` (download_s3_csv.py)
  - `zipfile` (download_s3_csv.py)
- No need to install additional dependencies

### DataFusion Python Version Scripts
- Python 3.6+
- Auto-install dependencies (first run):
  - `datafusion>=42.0.0`
  - `pandas>=2.0.0`
  - `pyarrow>=14.0.0`
- Uses `requirements.txt` to manage dependency versions

**When to Use DataFusion Python Version:** ⭐⭐ Highly Recommended
- ✅ **Any scenario** (first choice)
- ✅ **First-time users or new users** (auto-installs dependencies)
- ✅ Process any file size
- ✅ Need fastest execution speed (~0.1s)
- ✅ Need SQL auditability
- ✅ CSV structure may change
- ✅ Cross-platform compatible

**When to Use Standard Version:**
- ✅ Zero-dependency environment (completely unable to install external packages)
- ✅ Restricted environment or temporary use
- ✅ As backup verification solution

---

### 4. analyze_gross_spend_datafusion.py ⭐⭐

**🎯 Key Purpose: Solve LLM Token Limit Problem**

When comparison reports contain hundreds or thousands of rows of data, LLM cannot directly read the complete CSV (exceeds 25,000 token limit). This script generates 10 summary CSV files (< 10KB), allowing LLM to efficiently analyze large-scale data.

**Why is this script needed?**
- ❌ **Problem**: 173-row comparison report = 10,000+ tokens, manual LLM analysis prone to errors
- ✅ **Solution**: DataFusion generates 10 summary dimensions, total < 10,000 tokens, 100% accurate

**Real Case Example:**
- Manual LLM analysis: CPM difference = -$44,786.38 ❌ **Wrong**
- DataFusion summary: CPM difference = -$41,422.14 ✅ **Correct**
- Reason for difference: Manual analysis incorrectly grouped data rows

**Features:**
- ✅ **10 predefined analysis dimensions** (SQL auto-generated)
- ✅ Global summary, grouped by Vendor/Paid Action/Click URL
- ✅ CPM vs CPI comparison
- ✅ Match status analysis (Perfect/Minor/Major Diff)
- ✅ Top 50 largest differences
- ✅ Duplicate record detection
- ✅ Daily/weekly trend analysis
- ✅ **Small files suitable for LLM reading and analysis**

**Prerequisites:**
1. Generated `gross_spend_comparison_report.csv` (via Step 2 script)
2. Auto-install dependencies (first run): datafusion, pandas, pyarrow

**Usage Example:**
```bash
# Generate 10 analysis dimensions from comparison report (auto-install dependencies)
python3 scripts/analyze_gross_spend_datafusion.py \
    ./tmp/textnow_gross_spend_comparison_report.csv \
    ./tmp/analysis

# Output: 10 CSV files to ./tmp/analysis/ directory
```

**Output: 10 CSV Files**

| File | Content | Token Usage | Rows |
|------|---------|-------------|------|
| `01_global_summary.csv` | Global summary statistics | ~200 | 1 |
| `02_by_vendor.csv` | Grouped by Vendor | ~500 | ~10 |
| `03_by_paid_action.csv` | Grouped by Paid Action | ~400 | ~10 |
| `04_cpm_vs_cpi.csv` | CPM vs CPI comparison | ~300 | 2 |
| `05_match_status.csv` | Match status analysis | ~400 | ~4 |
| `06_top50_anomalies.csv` | Top 50 largest differences | ~3,000 | 50 |
| `07_by_click_url.csv` | Summarized by Click URL | ~1,500 | ~30 |
| `08_daily_trend.csv` | Daily trend | ~1,500 | ~30 |
| `09_duplicates.csv` | Duplicate record detection | ~500 | ~20 |
| `10_weekly_trend.csv` | Weekly summary | ~500 | ~5 |

**Total Token Usage: ~8,800** (well below 25,000 limit) ✅

**Terminal Output Example:**
```
============================================================
DataFusion Gross Spend Analysis
============================================================
Input:  ./tmp/textnow_gross_spend_comparison_report.csv
Output: ./tmp/analysis/

Generating analysis reports...

  ✓ Global Summary
  ✓ By Vendor
  ✓ By Paid Action
  ✓ CPM vs CPI
  ✓ Match Status
  ✓ Top 50 Anomalies
  ✓ By Click URL
  ✓ Daily Trend
  ✓ Duplicates
  ✓ Weekly Trend

============================================================
Analysis Complete
============================================================

Total Rows:        173
Campaigns:         9
Vendors:           7
Date Range:        25 days
Total Events:      3452
Calculated Spend:  $26248.56
Direct Spend:      $71075.94
Difference:        $-44827.38 (-63.07%)

✓ All reports generated in: ./tmp/analysis/
```

**Generated CSV Example (02_by_vendor.csv):**
```csv
vendor_name,rows,campaigns,events,calculated,direct,diff,diff_pct
Jampp,50,2,0,0.0,41422.14,-41422.14,-100.0
Kaden,55,2,1506,11639.4,15058.8,-3419.4,-22.71
Tapjoy,25,1,416,3120.0,3120.0,0.0,0.0
KyPI,19,1,914,6855.0,6862.5,-7.5,-0.11
```

**Complete Workflow (Recommended):**

```bash
# Step 1: Download data files
python3 scripts/download_s3_csv.py "<textnow_adjust_reports_url>" --output-dir ./tmp
python3 scripts/download_s3_csv.py "<click_url_histories_url>" --output-dir ./tmp
python3 scripts/download_s3_csv.py "<direct_spends_url>" --output-dir ./tmp

# Step 2: Generate detailed comparison report (173 rows, 10,000+ tokens)
python3 scripts/calculate_gross_spend_datafusion.py \
    ./tmp/textnow_adjust_reports_2026-01-01_2026-01-25.csv \
    ./tmp/click_url_histories_2026-01-01_2026-01-25.csv \
    ./tmp/direct_spends_2026-01-01_2026-01-25.csv \
    ./tmp/textnow_gross_spend_comparison_report.csv

# Step 3: Generate summary analysis (10 files, 8,800 tokens) ⭐⭐ Recommended for LLM analysis
python3 scripts/analyze_gross_spend_datafusion.py \
    ./tmp/textnow_gross_spend_comparison_report.csv \
    ./tmp/analysis

# Step 4: LLM analysis (read summary files)
# LLM can easily read ./tmp/analysis/*.csv files
# No need to read 173 complete rows
```

**LLM Analysis Workflow:**

```bash
# Quick overview of overall situation
cat ./tmp/analysis/01_global_summary.csv

# Identify problem sources
cat ./tmp/analysis/02_by_vendor.csv
cat ./tmp/analysis/04_cpm_vs_cpi.csv

# Focus on severe issues
cat ./tmp/analysis/06_top50_anomalies.csv
```

**Comparison: Without vs With Summary Script**

| Scenario | Without Summary | With Summary Script |
|----------|----------------|---------------------|
| **LLM Token Usage** | 10,000+ (may exceed limit) | 8,800 ✅ |
| **Accuracy** | Manual calculation error-prone | 100% SQL accurate |
| **Scalability** | <500 rows data | Supports millions of rows |
| **Analysis Speed** | Multiple reads + calculations | One generation, multi-dimensional |

**Use Cases:**
- ✅ **Any data volume > 100 rows** report analysis
- ✅ Let LLM perform business analysis (not math calculations)
- ✅ Identify systemic issues (like specific Vendor patterns)
- ✅ Generate management reports
- ✅ Investigate large differences
- ✅ Trend monitoring and alerts

---

## Maintainers

FeedMob Reporting Team

For questions or suggestions, please contact the team or create an issue.
