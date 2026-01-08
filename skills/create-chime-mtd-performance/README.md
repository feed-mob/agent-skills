# Create Chime MTD Performance Skill

## Overview

This skill automates the creation of new MTD (Month-to-Date) Performance data blocks in FeedMob's Chime Internal Pacing Sheet. It asks the user for the block size, copies the most recent data block from the top of the sheet, and updates the date range to reflect the current tracking period.

## Key Features

✨ **User-Guided Block Size** - Asks user for row count, eliminating complex detection logic
✨ **Fast Processing** - No need to read and analyze 50+ rows
✨ **Automated Data Copying** - Duplicates entire data blocks with formatting preserved
✨ **Smart Insertion** - Inserts new rows at the top without data loss
✨ **Date Management** - Automatically updates date ranges to reflect current period
✨ **Error Handling** - Includes validation and safeguards

## Files in This Skill

### 1. `SKILL.md`
The main skill definition document describing:
- Overall purpose and workflow
- Step-by-step instructions
- Important notes and best practices
- Target sheet information

### 2. `IMPLEMENTATION.md`
Detailed technical implementation guide including:
- Complete pseudo-code for the automation logic
- Helper functions for block detection
- Data analysis algorithms
- Error handling procedures
- Verification checklist

### 3. `QUICK_REFERENCE.md`
Quick reference guide for:
- 6-step process overview
- Data block structure patterns
- Common challenges and solutions
- Before/after examples
- Success indicators

### 4. `README.md` (this file)
Overview and navigation guide for the skill

## Use Cases

### Primary Use Cases
- **Monthly Transitions** - Create new MTD blocks at the start of each month
- **Daily Updates** - Refresh MTD data with new tracking dates
- **Automated Reporting** - Part of monthly report generation pipeline
- **Data Organization** - Keep most recent data at the top of sheet

### Supported Campaigns
- Samsung
- PerforMarkt
- Pointblank
- AdsPostX
- True Finance
- T-Mobile
- Thanks.co

### Supported Platforms
- Android
- iOS
- Web
- TV Universal

## Quick Start

### For Users
1. Read `QUICK_REFERENCE.md` for a 30-second overview
2. Understand the 6-step process
3. Learn what to look for in the data structure
4. Execute with Claude in Chrome browser extension

### For Developers/Implementers
1. Read `SKILL.md` for workflow overview
2. Study `IMPLEMENTATION.md` for technical details
3. Review the pseudo-code and helper functions
4. Implement using your preferred automation tool
5. Refer to error handling section for edge cases

## The 6-Step Automation Process

```
1. Open Sheet         → Navigate to Chime Internal Pacing Sheet
2. Ask User           → Prompt for number of rows to copy (e.g., 17)
3. Copy Block         → Select and copy rows 1 to user-specified row
4. Insert & Paste     → Insert copied rows at top
5. Update Date        → Replace A1 with MTD date range (month start - yesterday)
6. Save              → Auto-save sheet
```

## Target Sheet

**Chime Internal Pacing Sheet**
```
URL: https://docs.google.com/spreadsheets/d/1lar11y52pOYfbzlequ6cgeB3aMzvDWbcjmpyoaHC8pc/edit?gid=57802555#gid=57802555
```

## Data Block Structure

### Header Format (Date Range Pattern)
```
[START_DATE]-[END_DATE]/YEAR
Example: "1/01-1/02/2026"
Format: M/D-M/D/YYYY or M/DD-M/DD/YYYY
```

### Typical Layout
```
Row 1:    1/01-1/02/2026          ← FIRST block header (MOST RECENT, 2 days)
Row 2:    MTD performance
Row 3:    [Column headers or empty]
Row 4-17: [Campaign data rows]
Row 18:   1/01-1/01/2026          ← SECOND block header (OLDER, 1 day)
Row 19:   MTD performance
Row 20+:  [Older campaign data]
```

**Critical Understanding**:
- Row 1 = Most recent data (widest date range)
- Subsequent blocks below = Historical data (narrower date ranges)
- No empty rows separate blocks - date range patterns are the delimiters

### Key Variables
- **blockStartRow** - Row number of header (ALWAYS 1 for most recent block)
- **userRowCount** - Number of rows user specified (e.g., 17)
- **blockHeight** - Same as userRowCount (e.g., 17 rows)

## How Block Size is Determined

The automation uses a user-guided approach:

1. **CRITICAL ASSUMPTION** - The most recent MTD block is ALWAYS at row 1
   - No searching needed for block start
   - Row 1 ALWAYS contains the date range pattern (e.g., "1/01-1/02/2026")
   - This is maintained by each operation pushing older data down

2. **User Input** - The user provides the block size:
   - Prompt: "How many rows should I copy?"
   - User knows their current data structure (typically 15-25 rows)
   - Example: User says "17" → Copy rows 1-17
   - This eliminates complex scanning and pattern detection logic

3. **Validation** - Simple checks:
   - Input must be a positive integer
   - If user is unsure, guidance is provided on how to count rows
   - Typical block sizes are 15-25 rows depending on campaign count

**Key Insight**: By asking the user, we eliminate the need to read 50+ rows, scan for date patterns, and handle edge cases. This makes the automation faster and more reliable.

## Date Update Logic

When updating the date in cell A1:

```
Today: January 8, 2026
Yesterday: January 7, 2026
Start date: January 1, 2026 (1st of yesterday's month)
End date: January 7, 2026 (yesterday)
Result in A1: "1/01-1/07/2026"
```

Date calculation rules:
- **Delete existing data** in A1 first
- **Start date**: Always the 1st day of yesterday's month
- **End date**: Yesterday's date
- **Format**: M/DD-M/DD/YYYY (no spaces around dash)

Examples:
- Yesterday = Jan 10, 2026 → Type: `1/01-1/10/2026`
- Yesterday = Jan 1, 2025 → Type: `1/01-1/01/2025`
- Yesterday = Feb 2, 2026 → Type: `2/01-2/02/2026`
- Yesterday = Dec 31, 2025 → Type: `12/01-12/31/2025`

## Error Handling

The automation includes safeguards for:

| Scenario | Handling |
|----------|----------|
| Invalid row count input | Re-prompt with guidance and examples |
| User unsure of row count | Provide instructions on how to count rows |
| Zero or negative row count | Validation error, request positive number |
| Date format mismatch | Detect and adapt to existing format |
| Copy/paste failure | Retry operation with verification |
| Sheet not accessible | Check permissions and authentication |

## Verification Checklist

Before considering the operation complete, verify:

- [ ] User provided valid row count
- [ ] Correct number of rows copied (matches user input)
- [ ] New block appears at row 1 of sheet
- [ ] All rows from original block are present (no missing data)
- [ ] All columns from original block are present
- [ ] Cell A1 header updated with yesterday's date
- [ ] Date format matches existing format in sheet
- [ ] Previous row 1 is now at row (userRowCount + 1)
- [ ] No data was lost or overwritten
- [ ] Sheet is saved successfully

## Common Patterns in Data

### Campaign Data Format
```
Campaign Name | Platform | Enrollments | Spend | Additional Metrics...
Samsung | Android | 1500 | $45,000 | ...
Samsung | iOS | 2100 | $63,000 | ...
PerforMarkt | Web | 980 | $15,400 | ...
```

### Date Range Format
```
Required format for block detection:
- "1/01-1/02/2026"     (M/D-M/D/YYYY format - required for detection)
- "12/1-12/31/2025"    (M/DD-M/DD/YYYY format - required for detection)

The pattern MUST include the full year at the end to be detected.
Block detection looks specifically for this pattern in column A.
```

## Related Skills

This skill integrates with:
- **feedmob-chime-report-downloader** - Downloads latest Chime Media Plan Reports
- Other FeedMob automation tools for data management

## Support & Troubleshooting

### If Unsure How Many Rows to Copy
1. Look at the Google Sheet
2. Find column A (first column)
3. Locate the SECOND date range pattern (e.g., row 18 might have "1/01-1/01/2026")
4. Count rows from row 1 to the row before the second pattern
5. Example: If second pattern is at row 18, first block = 17 rows
6. Typical block sizes: 15-25 rows

### If Data Doesn't Copy or Paste Correctly
1. **Selection Issue**: Make sure you selected entire ROWS (click row numbers), not cells
2. **Copy Verification**: After Ctrl+C, look for moving dotted border (marching ants)
3. **Insert Method**: Use "Insert X copied rows above" - NOT regular paste (Ctrl+V)
4. **Context Menu**: Right-click on ROW NUMBER (not cells) to see "Insert copied rows" option
5. **Hidden Content**: Verify no rows/columns are hidden
6. **Protection**: Check that rows aren't protected from editing
7. **If Formatting Lost**: Always copy ROWS not cells - click row numbers on left side

### If Date Format is Wrong
1. Check format of other MTD blocks in sheet
2. Match that format exactly
3. Ensure date calculation is correct (yesterday's date)
4. Verify no extra characters or spaces

### Sheet Access Issues
1. Confirm you're logged into correct Google account
2. Check that you have edit permissions on sheet
3. Verify sheet isn't in read-only mode
4. Contact FeedMob admin if access denied

## Performance Notes

- **User Input**: Instant - no need to read/analyze rows
- **Copy/Paste**: Operation time depends on block size (usually <5 seconds)
- **Date Update**: Minimal processing, near-instantaneous
- **Save**: May take 1-2 seconds for sheet to save
- **Overall**: Significantly faster than previous approach (no 50-row scan needed)

## Future Enhancements

Potential improvements:
- [ ] Support for multiple MTD blocks in single operation
- [ ] Automatic backup creation before operation
- [ ] Email notification upon completion
- [ ] Scheduling for automatic monthly execution
- [ ] Custom date range calculation
- [ ] Block validation and quality checks

## Document Navigation

**For Quick Overview:**
→ Start with `QUICK_REFERENCE.md`

**For Full Instructions:**
→ Read `SKILL.md`

**For Technical Implementation:**
→ Study `IMPLEMENTATION.md`

**For This Overview:**
→ You're reading `README.md`

## Version History

**v1.0** (Current)
- Initial skill creation
- Full workflow documentation
- Comprehensive error handling
- Quick reference guide

## License & Usage

This skill is designed for FeedMob internal use. All workflows operate on FeedMob's Chime Internal Pacing Sheet.

## Questions or Issues?

Refer to the appropriate document:
- "How does it work?" → `SKILL.md`
- "How do I use it?" → `QUICK_REFERENCE.md`
- "How do I implement it?" → `IMPLEMENTATION.md`
- "What's the technical approach?" → `IMPLEMENTATION.md` (pseudo-code section)

---

**Last Updated:** January 2026
**Status:** Active
**Maintainer:** FeedMob Team
