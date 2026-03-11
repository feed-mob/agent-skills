# Report Structure Guide

This guide defines the standard structure for FeedMob spend verification reports.

---

## Report Organization Principles

When generating spend verification reports, you MUST organize them by **CPM vs Non-CPM** activities:

- **Non-CPM Activities**: CPI/CPA/CPC campaigns that can be verified using the formula `client_paid_action_count × gross_cpi`
- **CPM Activities**: Vendor-managed campaigns billed by impressions, marked with `client_paid_action = "vendor_managed"` and `gross_cpi = -1`

---

## Standard Report Structure

### 1. Overall Summary

Display high-level totals across all activities:

```
Total Click URLs: X
Total Calculated Gross Spend: $X,XXX.XX
Total Direct Gross Spend: $X,XXX.XX
Total Difference: $XXX.XX (X.X%)
Total Events: X,XXX
```

---

### 2. Non-CPM Activity Comparison (Primary Focus)

This is the main verification section showing verifiable CPI/CPA/CPC activities.

#### 2.1 Click URL Level Comparison Table (Sorted by Calculated Gross DESC)

```
| Click URL | Campaign | Vendor | Paid Action | Events | Calculated | Direct | Difference | Diff % | Status |
|-----------|----------|--------|-------------|--------|-----------|--------|-----------|--------|--------|
| 21337 | Campaign_A | Vendor_A | tutorial | 499 | $3,742.50 | $3,750.00 | -$7.50 | -0.20% | ✅ |
| 21306 | Campaign_B | Vendor_B | tutorial | 251 | $1,882.50 | $1,882.50 | $0.00 | 0.00% | ✅ |
```

**Columns:**
- **Click URL**: Unique campaign identifier
- **Campaign**: Campaign name
- **Vendor**: Traffic source vendor
- **Paid Action**: Event type used for billing (from `client_paid_action`)
- **Events**: Count of paid action events
- **Calculated**: Expected spend = `event_count × gross_cpi`
- **Direct**: Actual spend from direct_spends records
- **Difference**: Calculated - Direct
- **Diff %**: Percentage difference
- **Status**: Visual indicator (see Status Icons below)

#### 2.2 Vendor Level Summary Table (Sorted by Calculated Gross DESC)

```
| Vendor | Click URLs | Events | Calculated | Direct | Difference | Diff % | Status |
|--------|-----------|--------|-----------|--------|-----------|--------|--------|
| Kaden | 2 | 378 | $2,941.68 | $2,941.68 | $0.00 | 0.00% | ✅ Perfect |
| KyPI | 1 | 499 | $3,742.50 | $3,750.00 | -$7.50 | -0.20% | ✅ Excellent |
```

**Aggregation:**
- Sum all metrics across click URLs for each vendor
- Useful for identifying which vendors have discrepancies

#### 2.3 Non-CPM Summary Statistics

```
Non-CPM Click URLs: X
Total Calculated Gross Spend: $X,XXX.XX
Total Direct Gross Spend: $X,XXX.XX
Total Difference: $XXX.XX (X.X%)
Perfect Match Click URLs: X (X.X%) ✅
```

---

### 3. CPM Activity Section (Separate Display)

CPM activities use `client_paid_action = "vendor_managed"` and `gross_cpi = -1`, cannot be verified using CPI formula.

#### 3.1 CPM Click URL List

```
| Click URL | Campaign | Vendor | Direct Gross | Note |
|-----------|----------|--------|-------------|------|
| 21512 | TextNow_Android_CPM | Jampp | $11,042.54 | Vendor-managed, billed by CPM |
| 21513 | TextNow_iOS_CPM | Jampp | $8,125.13 | Vendor-managed, billed by CPM |
```

**Note:**
- No "Calculated" column (cannot calculate without CPM rates)
- Only show Direct Spend
- Add explanatory note about vendor management

#### 3.2 CPM Summary

```
CPM Click URLs: X
CPM Total Direct Gross: $X,XXX.XX
Note: CPM activities are vendor-managed, billed by impressions (impressions / 1000 × CPM_rate)
Recommendation: Verify separately with vendor or accept Direct Spend records
```

---

### 4. Verification Accuracy Statistics (Non-CPM Only)

```
| Accuracy Level | Click URL Count | Percentage | Total Amount |
|----------------|----------------|------------|-------------|
| Perfect Match (0% diff) | X | XX.X% | $X,XXX.XX |
| Excellent (<1% diff) | X | XX.X% | $X,XXX.XX |
| Good (<2% diff) | X | XX.X% | $X,XXX.XX |
| Needs Attention (≥2% diff) | X | XX.X% | $X,XXX.XX |

Verified Activities Accuracy: X/X = XX.X% ✅
```

**Accuracy Levels:**
- **Perfect Match**: 0% difference (calculated = direct)
- **Excellent**: < 1% difference
- **Good**: 1-2% difference
- **Needs Attention**: ≥ 2% difference

---

### 5. Key Findings and Recommendations

Provide actionable insights:

- List top performing Click URLs and Vendors (by accuracy)
- Flag Click URLs or Vendors with significant discrepancies
- Provide specific action items:
  - "Investigate Click URL 12345 - 15% overspend"
  - "Excellent performance from Vendor X - all campaigns within 1%"
  - "Configure missing rates for Click URLs: [list]"

---

## Status Icons

Use these visual indicators in tables:

- ✅ **Perfect/Excellent**: 0-1% difference
- ⚠️ **Good**: 1-2% difference
- 🚨 **Needs Attention**: ≥2% difference
- ℹ️ **New Activity**: No Direct Spend record (first-time campaign)

---

## Report Filtering Rules

Apply these rules when generating reports:

### Sorting:
- **Click URL Table**: Sort by Calculated Gross spend (descending)
- **Vendor Table**: Sort by Calculated Gross spend (descending)
- **Accuracy Stats**: Sort by accuracy level (best to worst)

### Filtering:
- **Filter out zero-activity rows**: Exclude rows where both Calculated and Direct are $0.00
- **Keep zero-conversion rows**: Include rows with $0.00 calculated but events exist (valid data)
- **Separate CPM**: CPM activities must be in separate section, not in accuracy calculations

### Grouping:
- **Non-CPM**: Group by CPI/CPA/CPC billing type
- **CPM**: Separate section with vendor-managed note

---

## Example Use Cases

### Example 1: TextNow Adjust Report
```
"Check TextNow Adjust report for 2026-01-01, display by CPM and Non-CPM categories"
```

**Expected Output:**
1. Overall summary with all TextNow click URLs
2. Non-CPM section showing tutorial/registration campaigns
3. CPM section showing Jampp impression-based campaigns
4. Accuracy statistics for Non-CPM only

### Example 2: Possible Finance Singular Report
```
"Compare Possible Finance Singular report, focus on click URL and vendor levels"
```

**Expected Output:**
1. Detailed click URL table with all campaigns
2. Vendor-level aggregation showing which vendors have discrepancies
3. Highlight any vendors with >2% difference

### Example 3: Multi-Client Report
```
"Verify TextNow spend, show CPI and CPM activities separately"
```

**Expected Output:**
1. Clear separation of verifiable (CPI) vs non-verifiable (CPM) campaigns
2. Different recommendations for each category
3. Accuracy stats only for CPI campaigns

---

## Report Generation Checklist

Before sending the final report, verify:

- [ ] Overall summary includes all click URLs (CPM + Non-CPM)
- [ ] Non-CPM activities have Click URL and Vendor tables
- [ ] CPM activities listed separately with explanatory notes
- [ ] Accuracy statistics exclude CPM activities
- [ ] Tables sorted correctly (by Calculated Gross DESC)
- [ ] Zero-activity rows filtered out ($0.00 calculated AND direct)
- [ ] Status icons applied correctly based on difference percentage
- [ ] Key findings section includes actionable recommendations
- [ ] All numbers traced back to DataFusion aggregation CSVs

---

## Common Mistakes to Avoid

❌ **Don't mix CPM and Non-CPM in the same accuracy calculations**
- CPM cannot be verified with CPI formula
- Must be separate sections with different recommendations

❌ **Don't filter out zero conversions**
- $0.00 calculated with events is valid data (no conversions occurred)
- Shows campaign was active but no qualifying events happened

❌ **Don't sort by Click URL ID**
- Sort by Calculated Gross to highlight high-spend campaigns first
- Users care most about large spend discrepancies

❌ **Don't forget vendor-level aggregation**
- Vendor table is critical for identifying systematic issues
- One vendor with consistent overspend = vendor relationship problem

❌ **Don't include CPM in "Perfect Match" counts**
- Perfect matches should only count verifiable (Non-CPM) campaigns
- CPM accuracy cannot be calculated without CPM rates
