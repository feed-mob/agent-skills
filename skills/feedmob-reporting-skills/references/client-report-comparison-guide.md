# Client Report Spend Comparison Guide

Compare client report `gross_spend` against FeedMob direct spend `feedmob_gross_spend`.

## Script

```bash
python3 scripts/compare_client_report_spend_datafusion.py \
    <client_report_spends.csv> <direct_spend.csv> <output.csv>
```

- Auto-installs dependencies (datafusion, pandas, pyarrow)
- Handles missing/empty direct spend file gracefully

## Comparison Modes

| Mode | Condition | Join Key |
|------|-----------|----------|
| Click URL level | `click_url_id` has data | `click_url_id + date` |
| Campaign level | `click_url_id` empty | `campaign_name` |

## Output Columns

| Column | Description |
|--------|-------------|
| `client_gross_spend` | From client report |
| `feedmob_gross_spend` | From direct spend |
| `feedmob_net_spend` | From direct spend |
| `difference` | `client - feedmob` |
| `difference_pct` | Percentage difference |
| `status` | ✅ Perfect (<$0.01) / ⚠️ Minor (<2%) / 🚨 Significant (≥2%) |

## MCP Tools

```javascript
// 1. Get available report names
mcp__feedmob-reporting__get_client_report_spend_report_names()

// 2. Fetch client report spends
mcp__feedmob-reporting__get_client_report_spends({
  start_date, end_date, report_name
})

// 3. Fetch direct spends
mcp__feedmob-reporting__get_direct_spends({
  start_date, end_date, client_id
})
```
