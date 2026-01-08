# Create Chime MTD Performance - Quick Reference

## What This Skill Does

Asks you for the data block size, then duplicates the most recent MTD Performance data block (which is ALWAYS at row 1) to create a new block at the top of the Chime Internal Pacing Sheet, updates its date range, and pushes all existing data down.

## When to Use

- Start of a new tracking period/month
- Need to create a fresh MTD block with today's date range
- Automating monthly report generation
- Quick data refresh without manual copying

## The 6-Step Process

### 1️⃣ Open Sheet
```
Action: Open new tab and navigate to Chime Internal Pacing Sheet
URL: https://docs.google.com/spreadsheets/d/1lar11y52pOYfbzlequ6cgeB3aMzvDWbcjmpyoaHC8pc/edit?gid=57802555#gid=57802555
Check: Sheet fully loaded
```

### 2️⃣ Ask User for Block Size
```
Action: Prompt "How many rows should I copy? (e.g., 17, 20, 25)"
Wait: User provides row count
Validate: Ensure it's a positive number
Example: User says "17" → Will copy rows 1-17

CRITICAL: Most recent block ALWAYS starts at row 1
Typical sizes: 15-25 rows depending on number of campaigns
```

### 3️⃣ Select and Copy Entire Rows
```
Selection:
  - Click row number 1 (left side gray area)
  - Hold Shift + Click row number specified by user (e.g., row 17)
  - Result: Rows 1-17 highlighted in blue/gray

Copy:
  - Press Ctrl+C (Windows) or Cmd+C (Mac)
  - OR Right-click → "Copy"
  - Verify: Moving dotted border appears (marching ants)

IMPORTANT: Select ROWS not cells - this preserves all formatting
```

### 4️⃣ Insert Copied Rows at Top
```
CRITICAL: Use "Insert copied rows above" feature

Method 1 (Recommended):
  1. Right-click on row number 1
  2. Select "Insert 17 copied rows above" (X = your block height)
  3. Done! This inserts AND pastes in one operation

Method 2 (Alternative):
  1. Right-click row 1 → "Insert X rows above"
  2. Click cell A1
  3. Press Ctrl+V or Cmd+V to paste

Verify:
  - New block appears at rows 1-17
  - Original block moved to rows 18-34
  - All formatting preserved
```

### 5️⃣ Update Date Range in A1
```
Edit:
  1. Click cell A1
  2. Press Delete or Backspace to clear existing data
  3. Calculate the new MTD date range:
     - Today: 1/8/2026 → Yesterday: 1/7/2026
     - Start date: 1st of yesterday's month = 1/01
     - End date: Yesterday's date = 1/07
  4. Type new date range: "1/01-1/07/2026"
  5. Press Enter

Format: M/DD-M/DD/YYYY (no spaces)

Examples:
  - Yesterday = Jan 10, 2026 → Type: "1/01-1/10/2026"
  - Yesterday = Jan 1, 2025 → Type: "1/01-1/01/2025"
  - Yesterday = Feb 2, 2026 → Type: "2/01-2/02/2026"

Verify:
  - A1 shows new date range
  - Format is M/DD-M/DD/YYYY (no spaces)
  - Start date is always 1st of the month
  - End date is yesterday's date
```

## Data Block Structure Pattern

```
Row 1:    1/01-1/02/2026                      ← FIRST block (MOST RECENT, 2 days)
Row 2:    MTD performance
Row 3:    [Column headers or empty]
Row 4-17: [Campaign data rows]
Row 18:   1/01-1/01/2026                      ← SECOND block (OLDER, 1 day)
Row 19:   MTD performance
Row 20+:  [Older campaign data]
```

**Key Understanding**:
- Row 1 = Most recent data (widest date range, e.g., 2 days: 1/01-1/02)
- Row 18+ = Older data (narrower date range, e.g., 1 day: 1/01-1/01)
- Date ranges get NARROWER as you go down (older = fewer days covered)

## What to Look For

### Header Characteristics
- ALWAYS in cell A1 for the most recent block
- Contains date range pattern in format "M/D-M/D/YYYY" or "M/DD-M/DD/YYYY"
- Examples: "1/01-1/02/2026" (2 days), "1/01-1/07/2026" (7 days)
- Must include full 4-digit year at the end
- Recent blocks have WIDER date ranges (more days)
- Older blocks have NARROWER date ranges (fewer days)

### Data Rows
- Multiple rows with campaign information below the header
- Consistent column structure across rows
- Usually 15-50 rows of campaign data per block
- May include platforms: Android, iOS, Web, TV Universal

### How to Determine Block Size
- Look at column A and find where the next date range pattern appears
- Count rows from row 1 to the row before the next date pattern
- Example: A1 has "1/01-1/02/2026", A18 has "1/01-1/01/2026" → First block = 17 rows
- If unsure, typical block sizes are 15-25 rows

## Date Calculation

Yesterday's date is calculated as:
```
Today's Date - 1 day

Example:
  Today: January 8, 2026
  Yesterday: January 7, 2026
  Format in cell: "1/7"
```

## Common Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Don't know how many rows to copy | Look at column A, find second date pattern, count rows from 1 to row before it |
| Unsure of block size | Typical: 15-25 rows; you can visually count the campaign data rows |
| Can't find date range pattern at A1 | Sheet structure is incorrect; verify this is the right sheet |
| Selected cells not rows | Click row NUMBERS (left gray area), not cells |
| Copy didn't work | Look for marching ants border after Ctrl+C |
| "Insert copied rows" not showing | Make sure you copied ROWS not cells; right-click on ROW number |
| Paste overwrote data | Use "Insert copied rows above" NOT regular paste |
| Formatting lost | Select entire ROWS before copying, not individual cells |
| Confused which block is newest | ALWAYS row 1 = newest (widest date range) |

## Variables to Track

```
blockStartRow     = ALWAYS 1 (most recent block is always at row 1)
userRowCount      = number of rows user specified (e.g., 17)
blockHeight       = same as userRowCount (e.g., 17 rows)
headerText        = original text in A1 before update
newHeaderText     = updated text with yesterday's date
```

## Before & After Example

### BEFORE (Today is 1/8/2026)
```
Row 1:  1/01-1/02/2026                      ← FIRST block (MOST RECENT, 2 days)
Row 2:  MTD performance
Row 3:  [data]
...
Row 17: [last row of data]
Row 18: 1/01-1/01/2026                      ← SECOND block (OLDER, 1 day)
Row 19: MTD performance
Row 20: [older data]
...
```

### AFTER (New block created with updated date)
```
Row 1:  1/01-1/07/2026                      ← NEW block (updated to yesterday)
Row 2:  MTD performance
Row 3:  [data - copied from original row 1 block]
...
Row 17: [last row of copied data]
Row 18: 1/01-1/02/2026                      ← ORIGINAL first block (pushed down)
Row 19: MTD performance
Row 20: [data]
...
Row 34: [end of original first block]
Row 35: 1/01-1/01/2026                      ← ORIGINAL second block (pushed down)
Row 36: MTD performance
...
```

**What Happened**:
1. Copied rows 1-17 (the most recent block)
2. Inserted them at the top
3. Updated A1 from "1/01-1/02/2026" to "1/01-1/07/2026"
4. Everything else shifted down by 17 rows

## Supported Campaign Partners

- Samsung
- PerforMarkt
- Pointblank
- AdsPostX
- True Finance
- T-Mobile
- Thanks.co

## Supported Platforms

- Android
- iOS
- Web
- TV Universal

## Sheet Access

**Required**: Google account with access to FeedMob's Chime Internal Pacing Sheet

If you get "Access Denied" error:
1. Check if you're logged into the correct Google account
2. Verify sheet sharing permissions
3. Contact FeedMob administrator if needed

## Success Indicators

✅ New block appears at row 1
✅ All data copied without loss
✅ Date updated to yesterday
✅ Original block pushed down
✅ Sheet saved successfully
✅ No error messages appear
