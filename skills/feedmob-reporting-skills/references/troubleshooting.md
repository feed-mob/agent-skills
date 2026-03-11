# Troubleshooting Guide

This guide covers common issues and their solutions when working with FeedMob reporting tools.

---

## Common Issues

### Missing click_url_ids
Some reports may not return click URL data for specific dates.

**Solutions:**
- Check if the campaign was active on the specified date
- Verify click URLs are correctly configured in the tracking system

### Report Delays
InMobi reports may take time to generate.

**Solutions:**
- Check report status before fetching
- Use `check_inmobi_report_status` tool to verify report is ready

### Rate Mismatches
Historical rates may differ from current rates.

**Solutions:**
- Always use dated rates from `get_click_url_histories`
- Always use `start_date` and `end_date` parameters when calling `get_click_url_histories`
- Never assume current rates apply to historical periods

### Empty Results
Date format or data availability issues.

**Solutions:**
- Ensure date format is exactly YYYY-MM-DD
- Check if campaigns were running on the specified dates
- Verify data exists in the attribution platform for that period

---

## Client-Specific Issues

### Missing client_paid_action Field
Some campaigns in click_url_histories may not return client_paid_action.

**Solutions:**
- Verify the campaign has a paid action configured
- Check click URL billing terms
- Flag for manual investigation
- Contact campaign manager to configure paid action

### Wrong Event Field Used
Using incorrect event counts (e.g., using `install` when client_paid_action is `tutorial`).

**Solutions:**
- **Always** check `client_paid_action` field first
- Never hard-code event field names
- Dynamically select event field based on `client_paid_action` value
- See [Anti-Hallucination Protocol](anti-hallucination-protocol.md) for verification steps

### Missing Event Data
Reports may not contain specified events for some click URLs.

**Solutions:**
- Verify events are correctly configured in attribution platform (Singular/Adjust)
- Check if event tracking is active
- Confirm event mapping is correct
- Review attribution platform logs for event receipt

### Different Paid Actions per Campaign
Each campaign may use different conversion events (determined by `client_paid_action`).

**Solutions:**
- This is **expected and correct behavior**
- Don't assume all campaigns use the same event type
- Don't hard-code event field names
- Always check `client_paid_action` for each click_url_id

### CPM Campaigns
CPM campaigns return `gross_cpi: -1` and cannot be verified using CPI formula.

**Solutions:**
- List CPM campaigns separately in reports
- Show Direct Spend only, no calculated spend
- Add note: "Vendor-managed, billed by CPM"
- Recommend verifying separately with vendor or accepting Direct Spend records

---

## Type Conversion Errors

### Type Mismatch Errors
Most common issue when calling multiple tools.

**Problem:**
- `get_click_url_histories` expects **number array**: `[12345, 12346]`
- `get_direct_spends` expects **string array**: `["12345", "12346"]`

**Solutions:**
- Remember the key difference
- Explicitly convert types when needed
- For direct spends: `click_url_ids.map(id => String(id))`
- For histories: `click_url_ids.map(id => Number(id))`

**Example:**
```javascript
// From CSV or attribution report
const click_url_ids = [12345, 12346]; // numbers

// Call histories (needs numbers) - OK as is
get_click_url_histories({ click_url_ids: click_url_ids });

// Call direct spends (needs strings) - convert first
get_direct_spends({ click_url_ids: click_url_ids.map(String) });
```

---

## Data Validation Issues

### Zero Conversions
Some click URLs may have zero tutorials/registrations/installs.

**Solutions:**
- This is **expected behavior**
- Include $0.00 calculated spend in reports
- **Don't** filter out zero-conversion click URLs
- Zero conversions are valid data points

### Missing Historical Rates
Some click URLs may not have rate data for specified dates.

**Solutions:**
- Report as "No rate data"
- Check if click URL was active on that date
- Verify rates were configured in the system at that time
- Contact campaign manager to add historical rates if needed

### Multiple Rows for Same (date, click_url_id)
Attribution reports may return multiple rows for the same click URL on the same date (different campaign variants, trackers, etc.).

**Solutions:**
- **Always aggregate** event counts before calculations
- Show aggregation work: "4+5=9" not just "9"
- See [Anti-Hallucination Protocol](anti-hallucination-protocol.md) for mandatory aggregation workflow

---

## MCP Tool Issues

### Tool Not Available
MCP tools fail or don't exist.

**Solutions:**
- Check if MCP server is configured correctly
- Verify `~/.claude/claude_desktop_config.json` includes feedmob-reporting-stage server
- Restart Claude Desktop after config changes
- Check MCP server logs for errors

### Tool Response Errors
Tool returns error messages instead of data.

**Solutions:**
- Check error message for specific issue
- Verify API credentials are valid
- Check date range is valid (not future dates)
- Verify click_url_ids exist in the system
- Check network connectivity

---

## CSV File Issues

### csv_file_path Not Available
Response doesn't include local CSV file path.

**Solutions:**
- Check if using old MCP version (only has s3_url)
- Fall back to downloading from s3_url
- Use `download_s3_csv.py` script to download and extract

### CSV Download Fails
S3 URL download errors.

**Solutions:**
- Check if S3 URL is valid and not expired
- Verify network connectivity
- Check if file exists on S3
- Use `--output-dir` parameter to specify writable directory

---

## Script Execution Issues

### Python Dependencies Not Found
`calculate_gross_spend_datafusion.py` or `analyze_gross_spend_datafusion.py` fails with missing dependencies.

**Solutions:**
Scripts auto-install dependencies. If auto-install fails:

```bash
# Manual dependency installation
pip install -r scripts/requirements.txt --user

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r scripts/requirements.txt
```

### Script Permission Denied
Cannot execute Python scripts.

**Solutions:**
```bash
# Add execute permission
chmod +x scripts/*.py

# Or run with python3 explicitly
python3 scripts/calculate_gross_spend_datafusion.py ...
```

### CSV Column Not Found
Script fails with "column not found" error.

**Solutions:**
- Verify CSV file has expected columns
- Check if CSV is from correct tool (Singular vs Adjust)
- Open CSV in text editor to inspect headers
- Ensure CSV is not empty or corrupted

---

## Report Generation Issues

### Numbers Don't Match
Calculated values differ from expected.

**Solutions:**
- **Re-read tool responses** - don't trust memory
- Verify aggregation of multiple rows
- Check correct formula is used: `client_paid_action_count × gross_cpi`
- Verify correct event field based on `client_paid_action`
- See [Anti-Hallucination Protocol](anti-hallucination-protocol.md) for complete verification workflow

### Missing Verification Steps
Report lacks raw data or aggregation tables.

**Solutions:**
- Never skip mandatory verification workflow
- Always show: Raw Data → Aggregation → Calculations → Final Report
- Include spot-check verification section
- See [Anti-Hallucination Protocol](anti-hallucination-protocol.md)

---

## When to Ask for Help

Contact the user or FeedMob team when:
- Client_paid_action is missing for multiple campaigns
- Event data consistently missing from attribution platform
- Large discrepancies (>10%) between calculated and direct spend
- MCP tools repeatedly fail with unclear errors
- Need to configure new client or campaign
- Historical rates are completely missing
