# AppsFlyer MMP Client Workflow

Use this universal workflow when a client uses AppsFlyer as MMP, but doesn't have a dedicated reporting API.

## Overview

**Applicable Scenarios:**
- Client's `mmp_track_party` field is `"appsflyer"`
- No dedicated API like Possible Finance (Singular), TextNow (Adjust)
- Need to use the universal `get_appsflyer_reports` tool

**Workflow Characteristics:**
- ✅ Universal: Applicable to any client using AppsFlyer MMP
- ✅ Consistent: Maintains consistency with other client workflows (Singular/Adjust)
- ✅ Flexible: Supports multiple filter options (client_ids, af_app_ids, campaign_ids, click_url_ids)

---

## Complete Process Example

**Scenario:** Verify gross spend for a client (e.g., "Example Client") during 2026-01-01 to 2026-01-05.

### Step 1: Query Client Information

```
mcp__feedmob-reporting__get_clients({
  client_name: "Example Client"  // Or omit parameter to get all clients
})
```

**Extract from Response:**
- Find target client record
- Check `mmp_track_party` field
- If `mmp_track_party === "appsflyer"`, extract `client_id`

**Example Response:**
```json
{
  "client_id": 123,
  "client_name": "Example Client",
  "mmp_track_party": "appsflyer",
  "status": "active"
}
```

### Step 2: Fetch AppsFlyer Reports

```
mcp__feedmob-reporting__get_appsflyer_reports({
  start_date: "2026-01-01",
  end_date: "2026-01-05",
  client_ids: ["123"]  // From Step 1
})
```

**Response Contains Fields:**
- `date`, `click_url_id`, `af_app_id`, `campaign_id`
- Event fields: `install`, `click`, `impression`, `registration`, `purchase`, etc.
- `csv_file_path` or `s3_url`

**Optional Filter Parameters:**
- `client_ids`: Filter by client ID (multiple supported)
- `af_app_ids`: Filter by AppsFlyer app ID
- `campaign_ids`: Filter by campaign ID
- `click_url_ids`: Filter by click URL ID

### Step 3-4: Fetch Historical Rates and Direct Spend (Parallel)

Same process as TextNow/Possible Finance:

```
// Call in parallel
mcp__feedmob-reporting__get_click_url_histories({
  click_url_ids: [click_url_ids extracted from AppsFlyer report - number array],
  start_date: "2026-01-01",
  end_date: "2026-01-05"
})

mcp__feedmob-reporting__get_direct_spends({
  start_date: "2026-01-01",
  end_date: "2026-01-05",
  click_url_ids: [click_url_ids extracted from AppsFlyer report - string array]
})
```

**Important:** Note the type differences:
- `get_click_url_histories` expects number array: `[12345, 12346]`
- `get_direct_spends` expects string array: `["12345", "12346"]`

### Step 5: Use DataFusion Script to Calculate Comparison

**Note: First use Glob to find `**/calculate_gross_spend_datafusion.py` to get full path**

```bash
python3 scripts/calculate_gross_spend_datafusion.py \
    ./tmp/appsflyer_reports_2026-01-01_2026-01-05.csv \
    ./tmp/click_url_histories_2026-01-01_2026-01-05.csv \
    ./tmp/direct_spends_2026-01-01_2026-01-05.csv \
    ./tmp/gross_spend_comparison_report.csv
```

### Step 6: Generate Multi-Dimensional Analysis Summary

**Note: First use Glob to find `**/analyze_gross_spend_datafusion.py` to get full path**

```bash
python3 scripts/analyze_gross_spend_datafusion.py \
    ./tmp/gross_spend_comparison_report.csv \
    ./tmp/analysis
```

### Step 7: Read Summary and Generate Report

Read the following CSV files:
- `01_global_summary.csv`
- `02_by_vendor.csv`
- `04_cpm_vs_cpi.csv`
- `07_by_click_url.csv`
- `08_daily_trend.csv`

Generate final report with same structure as TextNow/Possible Finance.

---

## AppsFlyer Special Considerations

### 1. Dynamic Client Detection
- ✅ Always call `get_clients` first to confirm MMP type
- ✅ Don't assume client uses AppsFlyer
- ✅ Check `mmp_track_party` field to confirm

### 2. Multi-Client Support
- ✅ `get_appsflyer_reports` supports multiple `client_ids`
- ✅ Can fetch data for multiple clients at once
- ✅ Suitable for batch analysis and comparison

### 3. Filter Options
- ✅ Use `af_app_ids`, `campaign_ids`, or `click_url_ids` for precise filtering
- ✅ If no filter parameters provided, returns all data
- ✅ Supports combining multiple filter conditions

### 4. Event Fields
- ✅ AppsFlyer report event fields similar to Singular
- ✅ Also uses `client_paid_action` for dynamic matching
- ✅ Common events: `install`, `registration`, `purchase`
- ✅ Supports custom event fields

---

## Complete Example: Chime Client

### Scenario
Verify gross spend for Chime client on 2026-01-01.

### Execution Steps

**1. Get Client Information**
```
mcp__feedmob-reporting__get_clients({ client_name: "Chime" })

Response:
{
  "id": 74,
  "name": "Chime",
  "mmp_track_party": "Appsflyer",
  "status": "normal"
}
```

**2. Fetch AppsFlyer Reports**
```
mcp__feedmob-reporting__get_appsflyer_reports({
  start_date: "2026-01-01",
  end_date: "2026-01-01",
  client_ids: ["74"]
})

Response: 5 click URLs, containing install, registration, purchase events, etc.
```

**3. Fetch Historical Rates and Direct Spend (Parallel)**
```
mcp__feedmob-reporting__get_click_url_histories({
  click_url_ids: [14727, 17083, 18894, 21580, 22287],
  start_date: "2026-01-01",
  end_date: "2026-01-01"
})

mcp__feedmob-reporting__get_direct_spends({
  start_date: "2026-01-01",
  end_date: "2026-01-01",
  click_url_ids: ["14727", "17083", "18894", "21580", "22287"]
})
```

**4. Calculate Comparison**
```bash
python3 scripts/calculate_gross_spend_datafusion.py \
    ./tmp/appsflyer_reports_2026-01-01.csv \
    ./tmp/click_url_histories_2026-01-01.csv \
    ./tmp/direct_spends_2026-01-01.csv \
    ./tmp/chime_gross_spend_comparison.csv
```

**5. Generate Analysis Summary**
```bash
python3 scripts/analyze_gross_spend_datafusion.py \
    ./tmp/chime_gross_spend_comparison.csv \
    ./tmp/chime_analysis
```

**6. LLM Reads Summary Files and Generates Report**
```
Read: ./tmp/chime_analysis/01_global_summary.csv
Read: ./tmp/chime_analysis/02_by_vendor.csv
Read: ./tmp/chime_analysis/04_cpm_vs_cpi.csv
Read: ./tmp/chime_analysis/07_by_click_url.csv
```

### Results
- Total Calculated Gross Spend: $10,803.50
- Total Direct Gross Spend: $29,784.50
- Total Difference: -$18,981.00 (-63.73%)
- Main Issue: Click URL 18894 (Samsung) has -$18,981 difference

---

## Comparison with Other Client Workflows

| Feature | Possible Finance | TextNow | AppsFlyer MMP Clients |
|---------|-----------------|---------|----------------------|
| **MMP Type** | Singular | Adjust | AppsFlyer |
| **Report API** | `get_possible_finance_singular_reports` | `get_textnow_adjust_reports` | `get_appsflyer_reports` |
| **Client Detection** | Not needed | Not needed | ✅ Must call `get_clients` first |
| **Filter Options** | None (fixed client) | None (fixed client) | ✅ Multiple filters (client_ids, af_app_ids, etc.) |
| **Event Fields** | Singular standard events | Adjust standard events | AppsFlyer standard events |
| **Subsequent Process** | Completely same | Completely same | Completely same |
| **Script Support** | ✅ Universal scripts | ✅ Universal scripts | ✅ Universal scripts |

**Key Advantages:**
- ✅ AppsFlyer MMP workflow is **universal**, applicable to any client using AppsFlyer
- ✅ Only need to add client detection in Step 1, remaining process completely consistent with other clients
- ✅ All scripts (calculate_gross_spend_datafusion.py, analyze_gross_spend_datafusion.py) are universal

---

## Common Questions

### Q1: How to determine if a client uses AppsFlyer?
**A:** Call `get_clients` and check the `mmp_track_party` field. If the value is `"appsflyer"` (case-insensitive), use this workflow.

### Q2: Can multiple AppsFlyer clients be analyzed simultaneously?
**A:** Yes! Pass multiple `client_ids` in `get_appsflyer_reports`:
```
client_ids: ["74", "123", "456"]
```

### Q3: What event fields does the AppsFlyer report contain?
**A:** Common fields include:
- `install` - Install event
- `registration` - Registration event
- `purchase` - Purchase event
- `click` - Click event
- `impression` - Impression event
- Custom events (based on client configuration)

Specific fields are dynamically matched via `client_paid_action`.

### Q4: What if a client uses multiple MMPs?
**A:** Currently each client has only one `mmp_track_party` field. If you need to analyze data from multiple MMPs, you need to call different reporting APIs separately.

### Q5: What's different between AppsFlyer workflow and Singular/Adjust?
**A:** Main differences are in Steps 1-2:
- AppsFlyer requires querying client information first to confirm MMP type
- Supports more flexible filter options
- Steps 3-7 are completely identical

---

## Related Documentation

- [Anti-Hallucination Protocol](anti-hallucination-protocol.md) - Ensure number accuracy
- [Report Structure Guide](report-structure.md) - Generate standardized reports
- [Troubleshooting Guide](troubleshooting.md) - Common issue solutions
- [MCP Tools Reference](mcp_tools.md) - Detailed descriptions of all available tools
