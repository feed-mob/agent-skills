# Calculation Verification Guide

This guide explains in detail how to match event fields and calculate expected Gross Spend, as well as the verification steps that must be followed.

## 🚨🚨🚨 Mandatory Formula Check

**STOP - Verify you're using the correct formula:**

✅ **Correct formula for all clients:**
```
calculated_gross_spend = client_paid_action_count × gross_cpi
```

Where `client_paid_action_count` is dynamically determined based on the `client_paid_action` field in click_url_histories.

---

## 🚨🚨🚨 Mandatory Verification Display

Before calculating anything, you **MUST** output the following verification sections to the user:

### Section A: Display Raw Data Rows

```markdown
## Raw Data from Attribution Report (Verification)

Display all rows for relevant click_url_ids:

Click URL 12345, Date 2025-12-25:
- Campaign: Campaign_A, tracker=tracker1, tutorial=120, registration=50, install=80

Click URL 12346, Date 2025-12-25:
- Campaign: Campaign_B_variant1, tracker=tracker2, tutorial=100, registration=30, install=45
- Campaign: Campaign_B_variant2, tracker=tracker2, tutorial=103, registration=25, install=40
[All relevant rows etc.]
```

### Section B: Display Aggregation Results

```markdown
## Aggregate Event Counts by (Date, Click URL)

| Date | Click URL | Tutorial | Registration | Install | [Other Events] |
|------|-----------|----------|--------------|---------|---------------|
| 2025-12-25 | 12345 | 120 | 50 | 80 | ... |
| 2025-12-25 | 12346 | 203 (100+103) | 55 (30+25) | 85 (45+40) | ... |

Note: Numbers in parentheses show individual row values being aggregated.
```

### Section C: Display Calculation Steps

```markdown
## Calculation Steps (client_paid_action × gross_cpi)

Click URL 12345 (client_paid_action="tutorial", gross_cpi=$12.50):
- 2025-12-25: 120 tutorials × $12.50 = $1,500.00

Click URL 12346 (client_paid_action="registration", gross_cpi=$11.80):
- 2025-12-25: 55 registrations × $11.80 = $649.00
```

**⚠️ Important: Only after displaying these three sections should you proceed to generate the final report table.**

---

## Detailed Calculation Steps

For each unique click_url_id and date combination:

### 1. Get client_paid_action
Retrieve the `client_paid_action` value from click_url_histories.

**Examples:**
- `"tutorial"` - Tutorial completion event
- `"registration"` - Registration event
- `"install"` - Installation event
- `"first_registration"` - First registration event
- `"first_install"` - First installation event

### 2. Aggregate Event Counts (Critical Step)

⚠️ **Critical**: The same click_url_id may appear multiple times on the same date in the attribution report, with different campaign names or trackers.

**You MUST aggregate all matching event fields before calculating:**
- Don't make up or guess numbers - use actual data from responses
- Show individual values being aggregated (like "100+103=203" not just "203")

**Example:**
```
Click URL 12346, Date 2025-12-25:
- Row 1: tutorial=100
- Row 2: tutorial=103
Aggregated: tutorial = 100 + 103 = 203
```

### 3. Match Event Field
Look up the event count corresponding to the `client_paid_action` field name in the attribution report response.

**Examples:**
- If `client_paid_action = "tutorial"`, use `report.tutorial`
- If `client_paid_action = "registration"`, use `report.registration`
- If `client_paid_action = "first_install"`, use `report.install` (remove "first_" prefix)

### 4. Get gross_cpi
Retrieve `gross_cpi` from historical rates (**NOT** `gross_rate`).

**Note:**
- Use `gross_cpi` field
- Unit: Dollars (USD)
- Example: `gross_cpi = 12.50` means $12.50 per event

### 5. Perform Calculation
```
calculated_gross_spend = client_paid_action_count × gross_cpi
```

**Example:**
```
client_paid_action_count = 120 tutorials
gross_cpi = $12.50
calculated_gross_spend = 120 × $12.50 = $1,500.00
```

### 6. Display Calculation Process
Show this calculation in your output before displaying the final table.

### 7. Double-Check Checklist
- [ ] Did you aggregate multiple rows for the same click_url_id?
- [ ] Did you use the correct event field?
- [ ] Did you use `gross_cpi` (not `gross_rate`)?
- [ ] Did you show the individual values being aggregated?
- [ ] Is the calculation formula `count × gross_cpi`?

---

## Handling Edge Cases

### 1. Missing Rate (gross_cpi = -1)
**Handling:** Report as "No rate data"

**Example:**
```
Click URL 12345: Cannot calculate (no rate data)
```

### 2. Missing client_paid_action
**Handling:** Mark as "Paid action not configured"

**Example:**
```
Click URL 12346: Paid action not configured (cannot determine billing event)
```

### 3. Event Field Not in Attribution Report
**Handling:** Mark as "Event not tracked"

**Example:**
```
Click URL 12347: tutorial event not tracked (field not in report)
```

### 4. Zero Event Count
**Handling:** Expected spend = 0

**Example:**
```
Click URL 12348: 0 events × $12.50 = $0.00
```

### 5. Click URL Missing in Histories
**Handling:** Flag for investigation

**Example:**
```
Click URL 12349: Present in attribution report but missing in histories (needs investigation)
```

---

## Complete Example: Possible Finance

### Scenario
Calculate gross spend for Possible Finance, date 2025-12-25.

### Input Data

**Singular Report:**
```json
[
  {
    "date": "2025-12-25",
    "click_url_id": 12345,
    "campaign": "Campaign_A",
    "tutorial": 120,
    "registration": 50,
    "install": 80
  },
  {
    "date": "2025-12-25",
    "click_url_id": 12346,
    "campaign": "Campaign_B_v1",
    "tutorial": 100,
    "registration": 30,
    "install": 45
  },
  {
    "date": "2025-12-25",
    "click_url_id": 12346,
    "campaign": "Campaign_B_v2",
    "tutorial": 103,
    "registration": 25,
    "install": 40
  }
]
```

**Click URL Histories:**
```json
[
  {
    "click_url_id": 12345,
    "date": "2025-12-25",
    "client_paid_action": "tutorial",
    "gross_cpi": 12.50
  },
  {
    "click_url_id": 12346,
    "date": "2025-12-25",
    "client_paid_action": "registration",
    "gross_cpi": 11.80
  }
]
```

### Verification Display

**Section A: Raw Data Rows**
```
Click URL 12345, Date 2025-12-25:
- Campaign: Campaign_A, tutorial=120, registration=50, install=80

Click URL 12346, Date 2025-12-25:
- Campaign: Campaign_B_v1, tutorial=100, registration=30, install=45
- Campaign: Campaign_B_v2, tutorial=103, registration=25, install=40
```

**Section B: Aggregation Results**
| Date | Click URL | Tutorial | Registration | Install |
|------|-----------|----------|--------------|---------|
| 2025-12-25 | 12345 | 120 | 50 | 80 |
| 2025-12-25 | 12346 | 203 (100+103) | 55 (30+25) | 85 (45+40) |

**Section C: Calculation Steps**
```
Click URL 12345 (client_paid_action="tutorial", gross_cpi=$12.50):
- 2025-12-25: 120 tutorials × $12.50 = $1,500.00

Click URL 12346 (client_paid_action="registration", gross_cpi=$11.80):
- 2025-12-25: 55 registrations × $11.80 = $649.00
```

### Final Results
| Click URL | Date | Event Type | Event Count | Gross CPI | Calculated Gross |
|-----------|------|------------|-------------|-----------|------------------|
| 12345 | 2025-12-25 | tutorial | 120 | $12.50 | $1,500.00 |
| 12346 | 2025-12-25 | registration | 55 | $11.80 | $649.00 |

**Total:** $2,149.00

---

## Relationship with Automation Scripts

When using DataFusion scripts, all the above calculation steps are completed automatically:

1. ✅ Automatically aggregates multiple rows for the same click_url_id
2. ✅ Automatically matches `client_paid_action` to event field
3. ✅ Automatically uses correct formula for calculation
4. ✅ Automatically handles edge cases

**However, the LLM still needs to:**
- Read the summary CSVs generated by the scripts
- Display verification sections (A, B, C)
- Generate business reports and recommendations

**References:**
- Script usage instructions: SKILL.md Step 3.5
- Anti-hallucination protocol: [anti-hallucination-protocol.md](anti-hallucination-protocol.md)

---

## Common Errors

### ❌ Error 1: Using gross_rate instead of gross_cpi
```
❌ calculated = 120 × 0.15 = 18.00  (used gross_rate)
✅ calculated = 120 × 12.50 = 1500.00  (correctly used gross_cpi)
```

### ❌ Error 2: Not aggregating multiple rows
```
❌ Click URL 12346: Using first row's tutorial=100
✅ Click URL 12346: Aggregated tutorial = 100 + 103 = 203
```

### ❌ Error 3: Hard-coding event field
```
❌ Assuming all clients use "tutorial"
✅ Dynamically read client_paid_action field
```

### ❌ Error 4: Skipping verification display
```
❌ Directly generating final report table
✅ First display sections A, B, C, then generate report
```

---

## Related Documentation

- [Anti-Hallucination Protocol](anti-hallucination-protocol.md) - Mandatory rules to prevent number hallucinations
- [Report Structure Guide](report-structure.md) - Report structure and format
- [AppsFlyer MMP Workflow](appsflyer-mmp-workflow.md) - AppsFlyer client workflow
- [Troubleshooting Guide](troubleshooting.md) - Common issue solutions
