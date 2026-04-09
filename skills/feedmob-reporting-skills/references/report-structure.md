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

CPM activities use `client_paid_action = "vendor_managed"` and `gross_cpi = -1`.

**When partner reports are available:** Gross spend can be calculated using `partner_net_spend × (1 - margin/100)`. In this case, vendor_managed campaigns appear in the Non-CPM comparison tables with `event_field = "partner_net_spend"` and are included in accuracy statistics.

**When partner reports are NOT available:** Cannot verify using CPI formula. Display separately as shown below.

#### 3.1 CPM Click URL List (Without Partner Report)

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

---

## Net Spend Report Structure

For partner reports (Jampp, Kayzen, YouAppi, Samsung, Smadex, InMobi, Liftoff), use this structure for net spend verification.

### Key Difference from Gross Spend

| Aspect | Gross Spend | Net Spend |
|--------|-------------|-----------|
| **Source** | Attribution Reports (Singular/Adjust) | Partner Reports |
| **Comparison** | `calculated_gross` vs `direct_gross` | `partner_net_spend` vs `feedmob_net_spend` |
| **Calculation** | `event_count × gross_cpi` | No calculation needed |
| **Rate Required** | Yes (`gross_cpi` from histories) | No |

---

### 1. Net Spend Overall Summary

```
Total Click URLs: X
Total Partner Net Spend: $X,XXX.XX
Total FeedMob Net Spend: $X,XXX.XX
Total Difference: $XXX.XX (X.X%)
Partner: [Jampp/Kayzen/YouAppi/etc.]
Date Range: YYYY-MM-DD to YYYY-MM-DD
```

---

### 2. Click URL Level Comparison Table

```
| Click URL | Campaign | Vendor | Date | Partner Net | FeedMob Net | Difference | Diff % | Status |
|-----------|----------|--------|------|-------------|-------------|------------|--------|--------|
| 12345 | Campaign_A | Jampp | 2025-01-01 | $1,500.00 | $1,500.00 | $0.00 | 0.00% | ✅ |
| 12346 | Campaign_B | Jampp | 2025-01-01 | $2,000.00 | $1,950.00 | $50.00 | 2.56% | 🚨 |
```

**Columns:**
- **Click URL**: Unique campaign identifier
- **Campaign**: Campaign name
- **Vendor**: Partner/vendor name
- **Date**: Report date
- **Partner Net**: Net spend from partner report (`partner_net_spend`)
- **FeedMob Net**: Net spend from FeedMob records (`feedmob_net_spend`)
- **Difference**: Partner Net - FeedMob Net
- **Diff %**: Percentage difference
- **Status**: Visual indicator (see Status Icons below)

---

### 3. Vendor Level Summary Table

```
| Vendor | Click URLs | Partner Net | FeedMob Net | Difference | Diff % | Status |
|--------|-----------|-------------|-------------|------------|--------|--------|
| Jampp | 5 | $15,000.00 | $14,950.00 | $50.00 | 0.33% | ✅ |
```

**Aggregation:**
- Sum all net spend across click URLs for each vendor
- Useful for identifying which vendors have discrepancies

---

### 4. Net Spend Verification Accuracy Statistics

```
| Accuracy Level | Click URL Count | Percentage | Total Amount |
|----------------|----------------|------------|-------------|
| Perfect (0%) | X | XX.X% | $X,XXX.XX |
| Excellent (<1%) | X | XX.X% | $X,XXX.XX |
| Good (1-2%) | X | XX.X% | $X,XXX.XX |
| Needs Attention (≥2%) | X | XX.X% | $X,XXX.XX |

Verified Accuracy: X/X = XX.X% ✅
```

**Accuracy Levels for Net Spend:**
- **Perfect**: 0% difference (partner = feedmob)
- **Excellent**: < 1% difference
- **Good**: 1-2% difference
- **Needs Attention**: ≥ 2% difference

---

### 5. Status Icons for Net Spend

Use these visual indicators in tables:

- ✅ **Perfect Match**: 0% difference
- ⚠️ **Minor Difference**: <2% difference
- 🚨 **Significant Difference**: ≥2% difference

---

### 6. Key Findings and Recommendations

Provide actionable insights:

- List top performing Click URLs and Vendors (by accuracy)
- Flag Click URLs or Vendors with significant discrepancies
- Identify:
  - **Partner-only entries**: Click URLs in partner report but not in FeedMob
  - **FeedMob-only entries**: Click URLs in FeedMob but not in partner report
- Provide specific action items:
  - "Investigate Click URL 12345 - $50 discrepancy"
  - "Excellent performance from Jampp - all campaigns within 1%"
  - "Missing FeedMob records for Click URLs: [list]"

---

### Net Spend Report Filtering Rules

Apply these rules when generating reports:

**Sorting:**
- **Click URL Table**: Sort by Absolute Difference (descending)
- **Vendor Table**: Sort by Total Partner Net Spend (descending)

**Filtering:**
- **Filter out zero-activity rows**: Exclude rows where both Partner Net and FeedMob Net are $0.00
- **Keep single-side entries**: Include rows where only one side has data (indicates missing records)

**Grouping:**
- Group by Click URL ID for aggregation across dates
- Group by Vendor for vendor-level analysis

---

### Example Net Spend Report Output

```
## Jampp Net Spend Verification Report
**Date Range:** 2025-01-01 to 2025-01-31

### Overall Summary
- Total Click URLs: 15
- Total Partner Net Spend: $45,234.56
- Total FeedMob Net Spend: $45,189.23
- Total Difference: $45.33 (0.10%)

### Verification Status
- ✅ Perfect Match: 10 campaigns (66.7%)
- ⚠️ Minor Difference (<2%): 4 campaigns (26.7%)
- 🚨 Significant Difference (≥2%): 1 campaign (6.6%)

### Anomalies
| Click URL | Date | Partner | FeedMob | Diff | Action |
|-----------|------|---------|---------|------|--------|
| 12346 | 2025-01-15 | $2,000.00 | $1,950.00 | $50.00 (2.56%) | Review billing |

### Key Findings
1. Excellent overall accuracy - 99.9% match
2. 1 campaign with >2% difference requires review
3. All discrepancies are in Jampp's favor (partner > feedmob)
```

