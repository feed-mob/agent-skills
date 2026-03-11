# Anti-Hallucination Protocol

## 📋 Why This Section Exists

**Real Incident:**
- User requested check of TextNow Adjust report data for click_url_id 20752
- Raw data clearly showed: `tutorial: 0` for all dates
- AI agent hallucinated "1 tutorial" and calculated $8.34 expected spend
- Final report showed false discrepancy: Expected $8.34 vs Actual $0.00
- **Root cause:** Agent didn't show raw data or aggregation steps before generating final report

**Solution:** Mandatory verification displays that make hallucinations visible and preventable.

---

## ⛔ Anti-Hallucination Rules

**Never:**
- ❌ Make up, guess, or estimate any numbers
- ❌ Calculate totals in your head - always aggregate from actual data
- ❌ Assume event counts without checking the actual response
- ❌ Skip aggregation steps when multiple rows exist
- ❌ Trust memory - always refer to tool response data
- ❌ Write numbers in reports without showing raw data sources

**Always:**
- ✅ Copy exact numbers from tool responses
- ✅ Show aggregation work step-by-step in output
- ✅ Verify every number against source data
- ✅ When in doubt, re-read tool responses
- ✅ Aggregate all rows with same (date, click_url_id) before calculations
- ✅ Create aggregation tables showing raw data before generating final reports
- ✅ Show your work: display intermediate calculations in output

---

## Mandatory Data Verification Workflow

Before generating any final report, you MUST:

### 1. First Create Raw Data Table

- Show all matching rows from tool responses
- Group by (date, click_url_id)
- Display all relevant fields: date, click_url_id, campaign_name, and all event counts
- This makes hallucinations visible and verifiable

### 2. Create Aggregation Table

- Show the sum for each event type per (date, click_url_id) combination
- Example format:
  ```
  ## Raw Data Aggregation (Verification Step)

  Click URL 20752 on 2026-01-02:
  - Row 1: campaign="..._20752", tutorial=0, registration=4, install=1
  - Row 2: campaign="..._FM", tutorial=0, registration=5, install=0
  - Total: tutorial=0, registration=9, install=1
  ```

### 3. Show Calculation Steps

- For each click_url_id and date, show:
  ```
  Click URL 20752, Date 2026-01-02:
  - client_paid_action: "tutorial" (from click_url_histories)
  - gross_cpi: $8.34 (from click_url_histories)
  - Event count (tutorial): 0 (from aggregation above)
  - Calculation: 0 × $8.34 = $0.00
  ```

### 4. Then Generate Final Report

- Use numbers from verification tables
- Reference back to verification sections
- If any number looks wrong, STOP and re-check raw data

**If you skip this verification workflow:**
- 🚨 You will hallucinate numbers
- 🚨 Users will lose trust in the analysis
- 🚨 Business decisions based on wrong data = serious consequences

---

## Example Correct Workflow Output

```markdown
## Step 1: Raw Data from Adjust Reports

[Show relevant raw data rows here]

## Step 2: Aggregate Data by (Date, Click URL)

Click URL 20752:
- 2026-01-01: tutorial=0, registration=10, install=1
- 2026-01-02: tutorial=0, registration=13, install=2
[etc...]

## Step 3: Calculation Steps

Click URL 20752 (client_paid_action="tutorial", gross_cpi=$8.34):
- 2026-01-01: 0 tutorials × $8.34 = $0.00
- 2026-01-02: 0 tutorials × $8.34 = $0.00
[etc...]

## Step 4: Final Comparison Report

[Now show final table using numbers from above]
```

---

## 🔄 Double-Check Mechanism - Mandatory Self-Verification

**Key: After creating verification tables but before generating final report, you MUST perform this self-check:**

### Self-Verification Protocol

**Step A: Re-read Tool Responses**
- Scroll up in conversation to find actual tool responses
- Don't trust memory or verification tables
- Look at the tool's raw JSON data

**Step B: Spot-check 3 Random Data Points**
- Pick 3 numbers from your verification table
- For each number, find the exact location in tool response JSON
- Verify they match exactly

**Spot-check Example:**
```
Spot-check #1:
- My verification table says: "Click URL 20752, tutorial=0"
- Check tool response line 402: "tutorial": 0  ✅ Match

Spot-check #2:
- My verification table says: "Click URL 20784, tutorial=7"
- Check tool response line 38: "tutorial": 7  ✅ Match

Spot-check #3:
- My aggregation says: "registration=9 (4+5)"
- Tool response row 1 line 405: "registration": 4
- Tool response row 2 line 414: "registration": 5
- Sum: 4 + 5 = 9  ✅ Match
```

**Step C: If Any Spot-check Fails**
- 🚨 Stop immediately
- 🚨 Don't proceed to generate final report
- 🚨 Re-create verification tables from scratch
- 🚨 Use Read tool to re-read tool responses if needed

**Step D: Document Your Spot-checks**
- Add brief section in output:
  ```markdown
  ## ✅ Self-Verification Completed

  Spot-checked 3 data points against raw tool responses:
  - Click URL 20752, tutorial count: ✅ Verified
  - Click URL 20784, tutorial count: ✅ Verified
  - Click URL 20752, registration sum (4+5=9): ✅ Verified

  All checks passed. Proceeding to generate final report.
  ```

**Why Double-Checking Matters:**
- Catches hallucinations in verification tables themselves
- Forces re-examination of source data
- Creates habit of checking before finalizing
- Gives users confidence that data was double-checked

**Red Flags That Should Trigger Extra Scrutiny:**
- 🚩 Any case where you're aggregating more than 3 numbers
- 🚩 Any click_url_id with more than 3 rows on the same date
- 🚩 Any calculation where the result "looks too high" or "looks too low"
- 🚩 Any zero values (verify they're actually zero, not missing data)
- 🚩 When you're processing more than 10 click_url_ids at once

---

## Client Detection and Formula Rules

**Before doing any calculations, you MUST identify the client and use the correct formula:**

### Client Detection Rules

- If user mentions **"TextNow"** or **"Adjust"** → Use TextNow workflow
- If user mentions **"Possible Finance"** or **"Singular"** → Use Possible Finance workflow
- If using **`get_textnow_adjust_reports`** → MUST use TextNow formula
- If using **`get_possible_finance_singular_reports`** → MUST use Possible Finance formula

### Formulas - Don't Mix Them Up

| Client | Tool | Event Field | Rate Field | Formula |
|--------|------|-------------|------------|---------|
| **TextNow** | `get_textnow_adjust_reports` | **`client_paid_action`** (dynamic) | **`gross_cpi`** | **`client_paid_action_count × gross_cpi`** |
| **Possible Finance** | `get_possible_finance_singular_reports` | **`client_paid_action`** (dynamic) | **`gross_cpi`** | **`client_paid_action_count × gross_cpi`** |

### Common Fatal Mistakes

- ❌ Hard-coding any event field name (`tutorial`, `registration`, `install`, etc.) - Must check `client_paid_action` first
- ❌ Using `gross_rate` (Wrong - Both clients use `gross_cpi`)
- ❌ Assuming any fixed event field without dynamically checking `client_paid_action`
- ❌ Using different formulas for different clients (Both use `client_paid_action_count × gross_cpi`)
- ❌ Assuming any client always uses the same event field (Wrong - It's dynamic per campaign)

### Verification Checklist - Complete Before Calculations

- [ ] I've identified which client this is (TextNow or Possible Finance)
- [ ] I've checked `client_paid_action` from click_url_histories to determine which event field to use
- [ ] I'm using dynamic event counts based on `client_paid_action` (not hard-coded field names)
- [ ] I'm using `gross_cpi` (not `gross_rate`) as the rate field
- [ ] I'm using the formula: `client_paid_action_count × gross_cpi` for both clients

---

## 🎯 Final Quality Checklist - Complete Before Sending Report

Before sending the final report to the user, verify all of these:

### Data Display Checklist
- [ ] ✅ I showed the **Raw Data Rows** section displaying actual tool response data
- [ ] ✅ I showed the **Aggregation Table** displaying sums by (date, click_url_id)
- [ ] ✅ I showed the **Calculation Steps** section displaying each multiplication
- [ ] ✅ Every number in my final report can be traced back to these verification sections

### Formula Verification Checklist
- [ ] ✅ I correctly identified the client (TextNow or Possible Finance)
- [ ] ✅ I checked `client_paid_action` in click_url_histories for each click_url_id
- [ ] ✅ I used event counts matching `client_paid_action` (not hard-coded fields)
- [ ] ✅ I used `gross_cpi` as the rate (not `gross_rate`)
- [ ] ✅ I used the formula: `client_paid_action_count × gross_cpi`

### Aggregation Verification Checklist
- [ ] ✅ I checked if any click_url_id appears multiple times on the same date
- [ ] ✅ If multiple rows exist, I aggregated event counts (shown in aggregation table)
- [ ] ✅ I showed the individual values being aggregated (like "0+0=0" or "4+5=9")
- [ ] ✅ I didn't make up, guess, or estimate any numbers

### Anti-Hallucination Verification
- [ ] ✅ I can point to the exact line in raw data for every number I used
- [ ] ✅ If user asks "where did you get this number?", I can answer immediately
- [ ] ✅ I didn't skip any verification display sections
- [ ] ✅ My verification sections appear BEFORE the final comparison table

### Double-Check Verification (Mandatory)
- [ ] ✅ I re-read the actual tool responses (not memory)
- [ ] ✅ I spot-checked 3 random data points
- [ ] ✅ All spot-checks matched tool responses exactly
- [ ] ✅ I documented spot-check results in output
- [ ] ✅ I included "Self-Verification Completed" section

### Output Structure Verification
- [ ] ✅ My response includes these sections in order:
  1. Raw Data from [Tool] Reports (Verification)
  2. Aggregate Event Counts by (Date, Click URL)
  3. Calculation Steps (client_paid_action × gross_cpi)
  4. Final Comparison Report

**If you can't check all boxes above:**
- 🚨 **DO NOT** send the report yet
- 🚨 Go back and add missing verification sections
- 🚨 Re-check your numbers against raw data
- 🚨 Show your work transparently

**Remember:** A report with visible verification is always better than a "clean" report with hidden calculations. Users need to trust the data, and transparency builds trust.

---

## 🔍 User Verification Guide

Include this section at the end of each report to help users verify your calculations:

```markdown
## 🔍 How to Verify This Report

If you want to double-check any numbers in this report:

### Verify Raw Data:
1. Tool responses are available in the conversation history above
2. Search for specific click_url_id and date in the JSON responses
3. Check if event counts match what I showed in the "Raw Data" section

### Verify Aggregation:
For click_url_ids with multiple rows:
1. Find all rows with the same (date, click_url_id) in raw data
2. Manually add up the event counts
3. Compare with my "Aggregation Table"

### Verify Calculations:
1. Take the aggregated event count from Step 2
2. Multiply by the gross_cpi from click_url_histories
3. Compare with my "Calculation Steps" section

### Quick Spot-check:
Pick any row from the final report and trace it backwards:
- Final Report → Calculation Steps → Aggregation Table → Raw Data → Tool Response

If any numbers don't match, let me know and I'll re-check the data.
```

**Why Provide This Guide:**
- Empowers users to verify independently
- Builds trust through transparency
- Catches any remaining errors through crowdsourcing
- Shows confidence in your work
- Makes it easy for users to report discrepancies
