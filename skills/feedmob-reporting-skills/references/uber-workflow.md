# Uber Technologies Workflow

Use this workflow for Uber Technologies gross spend verification using agency_conversion_records.

## Overview

**Client:** Uber Technologies
**Data Source:** Agency Conversion Records (via MCP)
**Key Difference:** Uses `get_agency_conversion_records` instead of Singular/Adjust reports

**After obtaining agency_conversion_records data, all subsequent steps (calculate gross spend, generate comparison) are identical to TextNow and Possible Finance workflows.**

---

## Complete Workflow

### Step 1: Get Client ID

First, retrieve the client_id for Uber Technologies:

```javascript
mcp__feedmob-reporting__get_clients({
  client_name: "Uber Technologies"
})
```

**Extract from response:**
- `client_id`: Uber Technologies client identifier

**Example Response:**
```json
{
  "status": 200,
  "data": [
    {
      "id": 123,
      "name": "Uber Technologies",
      "status": "active",
      "mmp_track_party": "appsflyer"
    }
  ]
}
```

---

### Step 2: Get Agency Conversion Records

Use the client_id to fetch agency conversion records:

**Option A: Filter by client_id (recommended for Uber)**
```javascript
mcp__feedmob-reporting__get_agency_conversion_records({
  client_id: 123,  // Uber Technologies client_id from Step 1
  date: "YYYY-MM-DD"  // optional
})
```

**Option B: Filter by specific click_url_ids**
```javascript
mcp__feedmob-reporting__get_agency_conversion_records({
  click_url_ids: [12345, 12346],  // number[]
  date: "YYYY-MM-DD"  // optional
})
```

**Parameters:**
- `client_id` (number, optional): Client ID to filter records
- `click_url_ids` (number[], optional): Array of click URL IDs to filter records
- `date` (string, optional): Date in YYYY-MM-DD format

**Note:** At least one filter parameter (`client_id` or `click_url_ids`) should be provided

**Returns:**
- Agency conversion records containing:
  - `click_url_id`: Click URL identifier
  - `date`: Record date
  - Event counts: `install`, `registration`, `tutorial`, `purchase`, etc.
  - Campaign information
  - `csv_file_path` or `s3_url`

**Response Structure:**
```json
{
  "status": 200,
  "data": {
    "csv_file_path": "/path/to/agency_conversion_records.csv",
    "s3_url": "https://s3.amazonaws.com/.../agency_conversion_records.zip",
    "records": [
      {
        "date": "2026-01-15",
        "click_url_id": 12345,
        "campaign_name": "Uber_iOS_US_CPI",
        "install": 120,
        "registration": 85,
        "tutorial": 50
      }
    ]
  }
}
```

**Save CSV File:**
- Use `csv_file_path` directly (preferred)
- Or download from `s3_url` if `csv_file_path` not available

---

### Step 2.5: Fetch Jampp Partner Report (For vendor_managed Campaigns)

If the click_url_histories from Step 3 contain entries with `client_paid_action = "vendor_managed"`, fetch the Jampp partner report for gross spend calculation.

```javascript
mcp__feedmob-reporting__get_jampp_reports({
  client_id: 123,  // Uber Technologies client_id from Step 1
  start_date: "2026-01-15",
  end_date: "2026-01-15"
})
```

**Why needed:** Vendor-managed campaigns use partner net spend and margin to calculate gross:
```
calculated_gross = partner_net_spend × (1 - margin/100)
```

**Save CSV File:**
- Save to `./tmp/jampp_reports_YYYY-MM-DD.csv`

---

### Step 3: Get Historical Rates and Direct Spend (Parallel)

**⚠️ From this point onwards, the workflow is IDENTICAL to TextNow and Possible Finance:**

Call both tools in parallel:

```javascript
// Tool 1: Get historical rates (number array)
mcp__feedmob-reporting__get_click_url_histories({
  click_url_ids: [12345, 12346],  // number[]
  start_date: "2026-01-15",
  end_date: "2026-01-15"
})

// Tool 2: Get direct spend (string array)
mcp__feedmob-reporting__get_direct_spends({
  start_date: "2026-01-15",
  end_date: "2026-01-15",
  click_url_ids: ["12345", "12346"]  // string[]
})
```

**Type Difference:**
- `get_click_url_histories`: expects **number[]** `[12345, 12346]`
- `get_direct_spends`: expects **string[]** `["12345", "12346"]`

---

### Step 4: Calculate Gross Spend Comparison

Use the DataFusion script (identical to other clients):

**First, use Glob to find the script:**
```bash
# Find script location
**/calculate_gross_spend_datafusion.py
```

**Then execute:**
```bash
# Without vendor_managed campaigns:
python3 scripts/calculate_gross_spend_datafusion.py \
    ./tmp/agency_conversion_records_2026-01-15.csv \
    ./tmp/click_url_histories_2026-01-15.csv \
    ./tmp/direct_spends_2026-01-15.csv \
    ./tmp/uber_gross_spend_comparison.csv

# With vendor_managed campaigns (add partner report CSV):
python3 scripts/calculate_gross_spend_datafusion.py \
    ./tmp/agency_conversion_records_2026-01-15.csv \
    ./tmp/click_url_histories_2026-01-15.csv \
    ./tmp/direct_spends_2026-01-15.csv \
    ./tmp/uber_gross_spend_comparison.csv \
    ./tmp/jampp_reports_2026-01-15.csv
```

**Features:**
- ✅ Uses formula: `client_paid_action_count × gross_cpi`
- ✅ For vendor_managed: `partner_net_spend × (1 - margin/100)`
- ✅ Dynamically matches event fields based on `client_paid_action`
- ✅ Automatically aggregates multiple rows
- ✅ Filters zero-activity records

---

### Step 5: Generate Multi-Dimensional Analysis Summary (Mandatory)

**First, use Glob to find the script:**
```bash
# Find script location
**/analyze_gross_spend_datafusion.py
```

**Then execute:**
```bash
python3 scripts/analyze_gross_spend_datafusion.py \
    ./tmp/uber_gross_spend_comparison.csv \
    ./tmp/uber_analysis
```

**Generates 10 summary dimensions:**
1. `01_global_summary.csv` - Global statistics
2. `02_by_vendor.csv` - Grouped by vendor
3. `03_by_paid_action.csv` - Grouped by paid action
4. `04_cpm_vs_cpi.csv` - CPM vs CPI comparison
5. `05_match_status.csv` - Match status analysis
6. `06_top50_anomalies.csv` - Top 50 largest discrepancies
7. `07_by_click_url.csv` - Grouped by click URL
8. `08_daily_trend.csv` - Daily trend
9. `09_duplicates.csv` - Duplicate detection
10. `10_weekly_trend.csv` - Weekly summary

**Total Token Usage:** ~8,800 (well below 25,000 limit)

---

### Step 6: LLM Analysis and Report Generation

**Prerequisites:**
- Step 5 completed successfully
- 10 summary CSV files generated

**Reading Order:**
1. Read global summary (1 row)
2. Read key groupings (~20 rows)
3. Read top anomalies (if discrepancies exist)
4. Read trend data
5. Generate business report

**Report Structure:**
Follow the standard format defined in [Report Structure Guide](report-structure.md):
1. Overall Summary
2. Non-CPM Activity Comparison (Click URL + Vendor tables)
3. CPM Activity Section (separate display)
4. Verification Accuracy Statistics (Non-CPM only)
5. Key Findings and Recommendations

---

## Key Differences from Other Clients

| Feature | Possible Finance | TextNow | **Uber Technologies** |
|---------|-----------------|---------|----------------------|
| **Data Source** | Singular API | Adjust API | **Agency Conversion Records** |
| **Step 1** | Direct API call | Direct API call | **Get client_id first** |
| **Step 2 Tool** | `get_possible_finance_singular_reports` | `get_textnow_adjust_reports` | **`get_agency_conversion_records`** |
| **Steps 3-6** | Standard workflow | Standard workflow | **Identical to others** |
| **Scripts** | ✅ Universal | ✅ Universal | ✅ **Same universal scripts** |

---

## Example: Complete Uber Workflow

```bash
# Step 1: Get Uber client_id (via MCP tool)
# Response: client_id = 123

# Step 2: Get agency conversion records
# API call returns csv_file_path: ./tmp/agency_conversion_records_2026-01-15.csv

# Step 2.5: Get Jampp partner report (if vendor_managed campaigns exist)
# API call returns csv_file_path: ./tmp/jampp_reports_2026-01-15.csv

# Step 3: Get historical rates and direct spend (parallel)
# Saves to: ./tmp/click_url_histories_2026-01-15.csv
#           ./tmp/direct_spends_2026-01-15.csv

# Step 4: Calculate comparison (with optional partner report)
python3 scripts/calculate_gross_spend_datafusion.py \
    ./tmp/agency_conversion_records_2026-01-15.csv \
    ./tmp/click_url_histories_2026-01-15.csv \
    ./tmp/direct_spends_2026-01-15.csv \
    ./tmp/uber_comparison.csv \
    ./tmp/jampp_reports_2026-01-15.csv

# Step 5: Generate analysis summaries (mandatory)
python3 scripts/analyze_gross_spend_datafusion.py \
    ./tmp/uber_comparison.csv \
    ./tmp/uber_analysis

# Step 6: LLM reads summaries and generates report
# Read: ./tmp/uber_analysis/*.csv
```

---

## Important Notes

### 1. Client ID is Required
- ✅ Always call `get_clients` first
- ✅ Extract `client_id` from response
- ✅ Use `client_id` to filter agency conversion records

### 2. Event Fields
- ✅ Agency conversion records contain standard event fields
- ✅ Same dynamic matching: use `client_paid_action` from click_url_histories
- ✅ Common events: `install`, `registration`, `tutorial`, `purchase`

### 3. Universal Scripts
- ✅ `calculate_gross_spend_datafusion.py` works with agency conversion records
- ✅ No code changes needed
- ✅ Automatically detects CSV structure

### 4. Formula Consistency
- ✅ Uses same formula: `client_paid_action_count × gross_cpi`
- ✅ Same validation rules apply
- ✅ Same anti-hallucination protocol

---

## Troubleshooting

### Q: What if agency_conversion_records returns no data?

**A:** Check:
- Verify click_url_ids are correct
- Confirm date range has data
- Check if campaigns were active during the period
- Verify agency conversion tracking is enabled

### Q: Can I query multiple dates at once?

**A:** The `date` parameter is optional:
- If provided: returns data for specific date
- If omitted: returns all available data (use date range filtering in analysis)

---

## Related Documentation

- [Anti-Hallucination Protocol](anti-hallucination-protocol.md) - Prevent number hallucinations
- [Calculation Verification Guide](calculation-verification-guide.md) - Calculation rules
- [Scripts Usage Guide](scripts-usage-guide.md) - Script documentation
- [Report Structure Guide](report-structure.md) - Report format standards
- [Data Collection Guide](data-collection-guide.md) - Data fetching best practices
