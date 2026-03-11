# Data Collection Guide

This guide details how to fetch attribution reports, historical rates, and Direct Spend data.

## Step 1: Fetch Attribution Report

### Choose Tool Based on Client

**Possible Finance (Singular):**
```
mcp__feedmob-reporting__get_possible_finance_singular_reports({
  start_date: "YYYY-MM-DD",
  end_date: "YYYY-MM-DD"
})
```

**TextNow (Adjust):**
```
mcp__feedmob-reporting__get_textnow_adjust_reports({
  start_date: "YYYY-MM-DD",
  end_date: "YYYY-MM-DD"
})
```

**Privacy Hawk (Singular):**
```
mcp__feedmob-reporting__get_privacy_hawk_singular_reports({
  start_date: "YYYY-MM-DD",
  end_date: "YYYY-MM-DD"
})
```

**AppsFlyer MMP Clients (Universal):**
For detailed process, see [AppsFlyer MMP Workflow](appsflyer-mmp-workflow.md)

### Extract Data from Response

**Common to all clients:**
- List of click_url_ids
- All event count columns (install, registration, purchase, etc.)
- Campaign names, channels, operating systems, etc.

### Data Validation

- Check if response is empty or contains errors
- Filter out null/undefined click_url_ids
- Verify all event counts are valid numbers
- Aggregate multiple rows by (date, click_url_id)

### Save Data Locally

**Priority Rules:**
1. Prefer using `csv_file_path` (new MCP version)
2. Fallback to downloading `s3_url` (old MCP version)

See complete documentation for detailed download process.

---

## Step 2: Fetch Historical Rates and Direct Spend

**Call two tools in parallel:**

```
mcp__feedmob-reporting__get_click_url_histories({
  click_url_ids: [number array],
  start_date: "YYYY-MM-DD",
  end_date: "YYYY-MM-DD"
})

mcp__feedmob-reporting__get_direct_spends({
  start_date: "YYYY-MM-DD",
  end_date: "YYYY-MM-DD",
  click_url_ids: [string array]
})
```

**Note Type Differences:**
- histories: number array `[12345, 12346]`
- direct_spends: string array `["12345", "12346"]`

---

## Related Documentation

- [AppsFlyer MMP Workflow](appsflyer-mmp-workflow.md)
- [Calculation Verification Guide](calculation-verification-guide.md)
