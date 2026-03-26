# FeedMob Reporting MCP Tools Reference

API reference for all feedmob-reporting MCP tools.

## Parameter Type Reference

**Critical:** Pay attention to parameter types to avoid errors:

| Tool | Parameter | Type | Format |
|------|-----------|------|--------|
| get_possible_finance_singular_reports | start_date, end_date | string | "YYYY-MM-DD" |
| get_koho_financial_singular_reports | start_date, end_date | string | "YYYY-MM-DD" |
| get_textnow_adjust_reports | start_date, end_date | string | "YYYY-MM-DD" |
| get_click_url_histories | click_url_ids | number[] | [12345, 12346] |
| get_click_url_histories | start_date | string | "YYYY-MM-DD" |
| get_click_url_histories | end_date | string | "YYYY-MM-DD" |
| get_direct_spends | click_url_ids | string[] | ["12345", "12346"] |
| get_direct_spends | start_date, end_date | string | "YYYY-MM-DD" |
| get_agency_conversion_records | client_id / click_url_ids | number / number[] | 123 / [12345, 12346] |
| create_direct_spend | click_url_id | number | 12345 |

## Table of Contents

1. [Possible Finance Tools](#possible-finance-tools)
2. [Koho Financial Tools](#koho-financial-tools)
3. [TextNow Tools](#textnow-tools)
4. [AppsFlyer Tools](#appsflyer-tools)
5. [Partner Reports (Net Spend)](#partner-reports-net-spend)
6. [Direct Spend Tools](#direct-spend-tools)
7. [AdOps Tools](#adops-tools)

---

## Possible Finance Tools

### get_possible_finance_singular_reports

Fetches Possible Finance Singular API reports for a specified date range.

**Parameters:**
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format

**Returns:**
- Array of report data containing:
  - `click_url_id`: The click URL identifier
  - **Event counts** (which one to use is determined by `client_paid_action` from click_url_histories):
    - `tutorial`: Number of tutorial completions
    - `registration`: Number of registrations
    - `install`: Number of installs
    - Other conversion events
  - `app_id`: Application identifier
  - `campaign_name`: Campaign name
  - Other Singular metrics

**Example:**
```javascript
mcp__feedmob-reporting__get_possible_finance_singular_reports({
  start_date: "2025-01-15",
  end_date: "2025-01-15"
})
```

**Common Use Cases:**
- Daily spend reconciliation for Possible Finance campaigns
- Conversion event tracking (tutorial, registration, install, etc.)
- Campaign performance analysis

**Important Notes:**
- **DO NOT assume any specific event is the conversion event** - the correct field is determined by `client_paid_action` from click_url_histories
- Different campaigns may use different conversion events (tutorial, registration, install, etc.)
- Always check `client_paid_action` first to know which event count to use for spend calculation

---

## Koho Financial Tools

### get_koho_financial_singular_reports

Fetches Koho Financial Singular API reports for a specified date range.

**Parameters:**
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format

**Returns:**
- Array of report data containing:
  - `click_url_id`: The click URL identifier
  - **Event counts** (which one to use is determined by `client_paid_action` from click_url_histories):
    - `tutorial`: Number of tutorial completions
    - `registration`: Number of registrations
    - `install`: Number of installs
    - Other conversion events
  - `app_id`: Application identifier
  - `campaign_name`: Campaign name
  - Other Singular metrics

**Example:**
```javascript
mcp__feedmob-reporting__get_koho_financial_singular_reports({
  start_date: "2025-01-15",
  end_date: "2025-01-15"
})
```

**Common Use Cases:**
- Daily spend reconciliation for Koho Financial campaigns
- Conversion event tracking (tutorial, registration, install, etc.)
- Campaign performance analysis

**Important Notes:**
- **DO NOT assume any specific event is the conversion event** - the correct field is determined by `client_paid_action` from click_url_histories
- Different campaigns may use different conversion events (tutorial, registration, install, etc.)
- Always check `client_paid_action` first to know which event count to use for spend calculation

---

## TextNow Tools

### get_textnow_adjust_reports

Fetches TextNow Adjust API reports for a specified date range.

**Parameters:**
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format

**Returns:**
- Array of report data containing:
  - `click_url_id`: The click URL identifier (may be null for some records)
  - **Event counts** (which one to use is determined by `client_paid_action` from click_url_histories):
    - `tutorial`: Number of tutorial completions
    - `registration`: Number of registrations
    - `install`: Number of installs
    - `retained`: Retention count
  - `adjust_campaign_name`: Adjust campaign name
  - `adjust_channel`: Traffic channel (jampp, tapjoy, glance, etc.)
  - `adjust_os_name`: Operating system (ios, android)
  - `date`: Report date
  - `impression`: Impression count
  - `click`: Click count

**Example:**
```javascript
mcp__feedmob-reporting__get_textnow_adjust_reports({
  start_date: "2025-12-25",
  end_date: "2025-12-25"
})
```

**Response Example:**
```json
{
  "status": 200,
  "data": {
    "adjust_reports": [
      {
        "date": "2025-12-25",
        "click_url_id": 21513,
        "tutorial": 62,
        "adjust_campaign_name": "TextNow_iOS_US_CPM_Agency_Jampp_FM",
        "adjust_channel": "jampp",
        "adjust_os_name": "ios",
        "impression": 1161694,
        "click": 11099,
        "install": 353
      }
    ]
  }
}
```

**Common Use Cases:**
- Daily spend reconciliation for TextNow campaigns
- Conversion event tracking (tutorial, registration, install, etc.)
- Campaign performance analysis
- Channel and OS performance comparison

**Important Notes:**
- **DO NOT hardcode which event field to use** - the correct field is determined by `client_paid_action` from click_url_histories
- Different campaigns may use different conversion events (tutorial, registration, install, etc.)
- `click_url_id` may be null for some records - filter these out before processing
- Multiple records may exist for the same click_url_id with different campaign names
- Consider aggregating event counts by click_url_id if needed
- Always check `client_paid_action` first to know which event count to use for spend calculation

---

## Agency Conversion Tools

### get_agency_conversion_records

Fetches agency conversion records for specified clients or click URLs.

**Primary Use Case:** Uber Technologies and other clients using agency conversion tracking.

**Parameters:**
- `client_id` (number, optional): Client ID to filter records
- `click_url_ids` (array of numbers, optional): Array of click URL IDs to filter records
- `date` (string, optional): Date in YYYY-MM-DD format

**Note:** At least one filter parameter (`client_id` or `click_url_ids`) should be provided.

**Returns:**
- Array of agency conversion records containing:
  - `click_url_id`: Click URL identifier
  - `date`: Record date
  - **Event counts** (which one to use is determined by `client_paid_action` from click_url_histories):
    - `install`: Number of installs
    - `registration`: Number of registrations
    - `tutorial`: Number of tutorial completions
    - `purchase`: Number of purchases
    - Other conversion events
  - `campaign_name`: Campaign name
  - `csv_file_path` or `s3_url`: Path to CSV data

**Example - Filter by client_id:**
```javascript
mcp__feedmob-reporting__get_agency_conversion_records({
  client_id: 123,  // Uber Technologies
  date: "2026-01-15"
})
```

**Example - Filter by click_url_ids:**
```javascript
mcp__feedmob-reporting__get_agency_conversion_records({
  click_url_ids: [12345, 12346],
  date: "2026-01-15"
})
```

**Response Example:**
```json
{
  "status": 200,
  "data": {
    "csv_file_path": "/tmp/agency_conversion_records_2026-01-15.csv",
    "s3_url": "https://s3.amazonaws.com/.../records.zip",
    "records": [
      {
        "date": "2026-01-15",
        "click_url_id": 12345,
        "campaign_name": "Uber_iOS_US_CPI",
        "install": 120,
        "registration": 85,
        "tutorial": 50,
        "purchase": 10
      }
    ]
  }
}
```

**Common Use Cases:**
- Uber Technologies gross spend verification
- Agency-managed campaign performance analysis
- Conversion event tracking for agency partners

**Important Notes:**
- **DO NOT assume any specific event is the conversion event** - the correct field is determined by `client_paid_action` from click_url_histories
- Different campaigns may use different conversion events (tutorial, registration, install, etc.)
- Always check `client_paid_action` first to know which event count to use for spend calculation
- After obtaining this data, follow the same workflow as TextNow/Possible Finance (Steps 3-6)

---

## AppsFlyer Tools

### get_appsflyer_reports

Retrieves AppsFlyer report data with optional filtering.

**Parameters:**
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format
- `af_app_ids` (array of strings, optional): Filter by AppsFlyer app IDs
- `click_url_ids` (array of strings, optional): Filter by click URL IDs

**Returns:**
- AppsFlyer report data including:
  - Conversion metrics
  - Attribution data
  - Click URL IDs
  - App performance data

**Example:**
```javascript
mcp__feedmob-reporting__get_appsflyer_reports({
  start_date: "2025-01-15",
  end_date: "2025-01-15",
  click_url_ids: ["123", "456"]
})
```

**Note:** You can filter by either af_app_ids, click_url_ids, or fetch all data by omitting filters.

---

## Partner Reports (Net Spend)

These tools fetch partner platform reports for net spend verification. Unlike gross spend verification (which requires calculation), net spend verification directly compares `partner_net_spend` vs `feedmob_net_spend`.

### Partner Reports Overview

| Partner | Tool | Workflow Type | client_id Required |
|---------|------|---------------|-------------------|
| Jampp | `get_jampp_reports` | Direct (1-step) | ✅ Yes |
| Kayzen | `get_kayzen_reports` | Direct (1-step) | ❌ No |
| YouAppi | `get_youappi_reports` | Direct (1-step) | ❌ No |
| Samsung | `get_samsung_reports` | Direct (1-step) | ❌ No |
| Smadex | `get_smadex_reports` | Multi-step | ❌ No |
| InMobi | `get_inmobi_reports` | Multi-step | ❌ No |
| Liftoff | `get_liftoff_reports` | Multi-step | ❌ No |

**Unified Response Field:** All partner reports return `partner_net_spend` for net spend amount.

---

### get_jampp_reports

Fetches Jampp report data for a specified date range.

**Parameters:**
- `client_id` (number, required): Client ID
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format

**Returns:**
- Array of report data containing:
  - `click_url_id`: The click URL identifier
  - `partner_net_spend`: Net spend from Jampp
  - `date`: Report date
  - Other Jampp-specific fields

**Example:**
```javascript
mcp__feedmob-reporting__get_jampp_reports({
  client_id: 123,
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})
```

**Common Use Cases:**
- Net spend verification for Jampp campaigns
- Daily/weekly/monthly reconciliation
- Campaign performance analysis

---

### get_kayzen_reports

Fetches Kayzen report data for a specified date range.

**Parameters:**
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format

**Returns:**
- Array of report data containing:
  - `click_url_id`: The click URL identifier
  - `partner_net_spend`: Net spend from Kayzen
  - `date`: Report date
  - Other Kayzen-specific fields

**Example:**
```javascript
mcp__feedmob-reporting__get_kayzen_reports({
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})
```

---

### get_youappi_reports

Fetches YouAppi report data for a specified date range.

**Parameters:**
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format

**Returns:**
- Array of report data containing:
  - `click_url_id`: The click URL identifier
  - `partner_net_spend`: Net spend from YouAppi
  - `date`: Report date
  - Other YouAppi-specific fields

**Example:**
```javascript
mcp__feedmob-reporting__get_youappi_reports({
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})
```

---

### get_samsung_reports

Fetches Samsung report data for a specified date range.

**Parameters:**
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format

**Returns:**
- Array of report data containing:
  - `click_url_id`: The click URL identifier
  - `partner_net_spend`: Net spend from Samsung
  - `date`: Report date
  - Other Samsung-specific fields

**Example:**
```javascript
mcp__feedmob-reporting__get_samsung_reports({
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})
```

---

### get_smadex_reports (Multi-step)

Fetches Smadex report data. Requires 3-step workflow.

**Step 1: Get Report IDs**
```javascript
mcp__feedmob-reporting__get_smadex_report_ids({
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})
```

**Step 2: Check Status (repeat until ready)**
```javascript
mcp__feedmob-reporting__check_smadex_report_status({
  report_id: "abc-123"
})
```

**Step 3: Get Report Data**
```javascript
mcp__feedmob-reporting__get_smadex_reports({
  report_id: "abc-123"
})
```

**Returns:**
- Array of report data containing:
  - `click_url_id`: The click URL identifier
  - `partner_net_spend`: Net spend from Smadex
  - `date`: Report date
  - Other Smadex-specific fields

---

### get_inmobi_reports (Multi-step)

Fetches InMobi report data. Requires 3-step workflow with SKAN and Non-SKAN reports.

**Step 1: Get Report IDs**
```javascript
mcp__feedmob-reporting__get_inmobi_report_ids({
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})
```

**Step 2: Check Status (repeat until ready)**
```javascript
mcp__feedmob-reporting__check_inmobi_report_status({
  report_id: "abc-123",
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})
```

**Step 3: Get Report Data**
```javascript
mcp__feedmob-reporting__get_inmobi_reports({
  skan_report_id: "skan-123",
  non_skan_report_id: "non-skan-456",
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})
```

**Returns:**
- Array of report data containing:
  - `click_url_id`: The click URL identifier
  - `partner_net_spend`: Net spend from InMobi
  - `date`: Report date
  - Other InMobi-specific fields

**Note:** InMobi returns two report types (SKAN and Non-SKAN) that should be combined for full coverage.

---

### get_liftoff_reports (Multi-step)

Fetches Liftoff report data. Requires 3-step workflow with Stash and Possible Finance reports.

**Step 1: Get Report IDs**
```javascript
mcp__feedmob-reporting__get_liftoff_report_ids({
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})
```

**Step 2: Check Status (repeat until ready)**
```javascript
mcp__feedmob-reporting__check_liftoff_report_status({
  stash_report_id: "stash-123",
  possible_finance_report_id: "pf-456"
})
```

**Step 3: Get Report Data**
```javascript
mcp__feedmob-reporting__get_liftoff_reports({
  stash_report_id: "stash-123",
  possible_finance_report_id: "pf-456",
  start_date: "2025-01-01",
  end_date: "2025-01-31"
})
```

**Returns:**
- Array of report data containing:
  - `click_url_id`: The click URL identifier
  - `partner_net_spend`: Net spend from Liftoff
  - `date`: Report date
  - Other Liftoff-specific fields

**Note:** Liftoff returns two report types (Stash and Possible Finance) that should be combined for full coverage.

---

## Direct Spend Tools

### get_direct_spends

Fetches direct spend data from FeedMob for specified click URLs.

**Parameters:**
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format
- `click_url_ids` (array of strings, required): Array of click URL IDs

**Returns:**
- Array of direct spend records containing:
  - `feedmob_click_url_id`: Click URL identifier (note the `feedmob_` prefix)
  - `campaign_name`: Campaign name
  - `date`: Date of the spend
  - `feedmob_gross_spend`: Gross spend amount
  - `feedmob_net_spend`: Net spend amount

**Example:**
```javascript
mcp__feedmob-reporting__get_direct_spends({
  start_date: "2025-12-25",
  end_date: "2025-12-25",
  click_url_ids: ["21513", "21512", "20784"]
})
```

**Response Example:**
```json
{
  "status": 200,
  "data": [
    {
      "feedmob_click_url_id": 20784,
      "campaign_name": "TextNow_Android_US_CPA_Agency",
      "date": "2025-12-25",
      "feedmob_net_spend": 24,
      "feedmob_gross_spend": 30
    }
  ]
}
```

**Common Use Case:** Comparing calculated spend vs. actual direct spend for reconciliation.

**Important Notes:**
- Field names have `feedmob_` prefix (e.g., `feedmob_gross_spend` not `gross_spend`)
- Use `feedmob_click_url_id` to match with other data sources

### get_click_url_histories

Fetches historical CPI (Cost Per Install) and rate data for click URLs.

**Parameters:**
- `click_url_ids` (array of numbers, required): Array of click URL IDs
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format

**Returns:**
- Historical rate data containing:
  - `click_url_id`: Click URL identifier
  - `client_paid_action`: Event type used for billing (e.g., "tutorial", "registration", "install")
  - `gross_cpi`: Historical gross CPI rate (not `gross_rate` or `gross_cpi_by_date`)
  - `net_cpi`: Historical net CPI rate (not `net_rate` or `net_cpi_by_date`)
  - `date`: Date of the rate

**Special Values:**
- `gross_cpi = -1`: Indicates no rate configured for this click_url_id on the specified date
  - Common for CPM campaigns that don't use CPI-based pricing
  - Cannot calculate expected spend when rate is -1

**Example:**
```javascript
mcp__feedmob-reporting__get_click_url_histories({
  click_url_ids: [21513, 21512, 20784],
  start_date: "2025-12-25",
  end_date: "2025-12-25"
})
```

**Response Example:**
```json
{
  "status": 200,
  "data": [
    {
      "click_url_id": 20784,
      "client_paid_action": "registration",
      "date": "2025-12-25",
      "gross_cpi": 7.5,
      "net_cpi": 6
    },
    {
      "click_url_id": 21337,
      "client_paid_action": "tutorial",
      "date": "2025-12-25",
      "gross_cpi": 8.5,
      "net_cpi": 6.8
    },
    {
      "click_url_id": 21513,
      "client_paid_action": null,
      "date": "2025-12-25",
      "gross_cpi": -1,
      "net_cpi": -1
    }
  ]
}
```

**Critical Use Case:** This is essential for calculating expected gross spend:
```
Step 1: Check client_paid_action to determine which event to use
Step 2: Get event count from Adjust reports (e.g., adjust_report[client_paid_action])
Step 3: Calculate: expected_gross_spend = event_count × gross_cpi
```

**Example Calculation:**
```
For click_url_id 20784:
- client_paid_action = "registration"
- Get adjust_report[20784].registration count = 15
- Calculate: 15 × 7.5 = $112.50
```

**Important Notes:**
- **`client_paid_action` is CRITICAL** - it tells you which event field to use from Adjust reports
- Different click URLs may use different conversion events
- Field names are `gross_cpi` and `net_cpi` (not `gross_rate` or `gross_cpi_by_date`)
- Always check for `-1` value before calculations
- Rate of `-1` typically indicates CPM campaigns or missing configuration

---

## AdOps Tools

### get_adops_reports

Retrieves AdOps monthly report data.

**Parameters:**
- `month` (string, required): Month in YYYY-MM format

**Returns:**
- Monthly AdOps report data

**Example:**
```javascript
mcp__feedmob-reporting__get_adops_reports({
  month: "2025-01"
})
```

---

## Quick Reference

**Key Formula:**
```
expected_gross_spend = client_paid_action_count × gross_cpi
```

**Type Reminders:**
- `get_click_url_histories`: number[] `[12345, 12346]`
- `get_direct_spends`: string[] `["12345", "12346"]`

**Date Format:** Always use `YYYY-MM-DD`

For detailed workflows, see SKILL.md.
