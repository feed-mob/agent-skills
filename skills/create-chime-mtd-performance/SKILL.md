---
name: create-chime-mtd-performance
description: Automated MTD Performance data block creation in Chime Internal Pacing Sheet. Asks user for block size, duplicates the top data block, and updates date ranges. Use at the start of new tracking periods for fast, accurate updates.
---

# Create Chime MTD Performance

This skill provides fast, user-guided automation for managing MTD (Month-to-Date) Performance data blocks in the Chime Internal Pacing Sheet. By asking the user for the block size, it eliminates complex detection logic and ensures accurate, quick updates.

## Target Sheet

Operations are performed on the Chime Internal Pacing Sheet:
https://docs.google.com/spreadsheets/d/1lar11y52pOYfbzlequ6cgeB3aMzvDWbcjmpyoaHC8pc/edit?gid=57802555#gid=57802555

## Workflow Overview

The automation follows this streamlined process:

### Step 1: Open and Access the Sheet
- Open a new browser tab
- Navigate to the target Google Sheet URL
- Ensure the sheet is fully loaded and accessible

### Step 2: Determine Block Size
- **CRITICAL RULE**: The most recent MTD Performance data block is ALWAYS at the top of the sheet (starting from row 1)
- **Ask the user**: "How many rows should I copy?" (e.g., 17, 20, 25)
  - The user knows their current data block size
  - Typical block sizes range from 15-25 rows depending on the number of campaigns
- **Block Structure**:
  - Row 1 contains the date range pattern "M/D-M/D/YYYY" (e.g., "1/01-1/02/2026")
  - Subsequent rows contain campaign data
- Once the user provides the row count, proceed to copy that many rows starting from row 1

### Step 3: Select and Copy the Data Block
**Selection:**
- Click on row number 1 (on the left side) to select the entire row 1
- Hold Shift and click on the row number provided by the user (e.g., row 17 if user said "17 rows")
  - Example: If user said 17 rows → Click row 1, hold Shift, click row 17 → Rows 1-17 are now selected
- **Important**: Always select from row 1, as this is where the most recent data resides
- Verify: All rows should be highlighted in blue/gray

**Copy:**
- Press Ctrl+C (Windows/Linux) or Cmd+C (Mac) to copy
- OR right-click on the selected rows and choose "Copy"
- Verify: You should see a moving dotted border around the selected rows (marching ants)

### Step 4: Insert Copied Rows at the Top
**CRITICAL: Use "Insert Copied Rows" NOT Regular Paste**

**Method 1 (Recommended):**
1. Right-click on row number 1 (the first row)
2. Select "Insert X copied rows above" from the context menu
   - X will be the number of rows you copied (e.g., "Insert 17 copied rows above")
3. This will insert the copied data AND shift all existing content down automatically

**Method 2 (Alternative):**
1. Right-click on row number 1
2. Select "Insert 1 row above" (repeat this X times where X = number of rows in the block)
3. After inserting empty rows, click cell A1
4. Press Ctrl+V (Windows/Linux) or Cmd+V (Mac) to paste

**Verification after insertion:**
- The new block should appear at rows 1-17 (or your block size)
- The original first block should now start at row 18 (or blockHeight + 1)
- All data should be intact with no overwriting

### Step 5: Update Date Range in A1
**Replace the Date Range:**
1. Click on cell A1 to select it
2. Press Delete or Backspace to clear the existing data
3. Calculate the new date range based on yesterday's date:
   - **Start Date**: Always the 1st day of yesterday's month
   - **End Date**: Yesterday's date
   - **Format**: M/DD-M/DD/YYYY (no spaces around the dash)
4. Type the new date range and press Enter

**Date Range Calculation Examples:**
- If yesterday is January 10, 2026 → Type: `1/01-1/10/2026`
- If yesterday is January 1, 2025 → Type: `1/01-1/01/2025`
- If yesterday is February 2, 2026 → Type: `2/01-2/02/2026`
- If yesterday is December 31, 2025 → Type: `12/01-12/31/2025`

**Complete Example:**
- Today: January 8, 2026
- Yesterday: January 7, 2026
- Start date: January 1, 2026 (1st of yesterday's month)
- End date: January 7, 2026 (yesterday)
- **Type in A1**: `1/01-1/07/2026`

**Verification:**
- Cell A1 shows the new date range
- Format is M/DD-M/DD/YYYY (no spaces)
- Start date is always the 1st of the month
- End date is yesterday's date
- Year is included at the end

## Data Block Characteristics

### Block Structure
- **Header Row**: Row 1 contains date range pattern "M/D-M/D/YYYY" in column A (e.g., "1/01-1/02/2026")
- **Campaign Data**: Subsequent rows contain campaign metrics (names, enrollments, spending, etc.)
- **Block Size**: Typically 15-25 rows depending on the number of active campaigns

### Example Structure
```
Row 1:   1/01-1/02/2026                      ← FIRST block (MOST RECENT) - starts here
Row 2:   MTD performance
Row 3:   [Column headers]
Row 4-17: [Campaign data rows]               ← User specifies this range (e.g., "17 rows")
Row 18:  1/01-1/01/2026                      ← SECOND block (OLDER)
Row 19+: [Older campaign data rows]
```

**Key Points**:
- Row 1 ALWAYS contains the most recent data block
- The user knows their current block size and will provide it when asked
- Each operation adds a new block at the top, pushing older blocks down

## Important Operational Notes

- **CRITICAL RULE**: The most recent data block ALWAYS starts at row 1
- **Block Position Logic**:
  - Row 1 = Most recent data (widest date range)
  - Rows below = Historical data (narrower date ranges)
  - Each new operation adds a newer block at the top, pushing older ones down
- **User Input**: Always ask the user for the number of rows to copy at Step 2
- **Data Integrity**: Verify the complete data block is selected before copying
- **Column Coverage**: Ensure all columns with data are included (select entire rows, not cells)
- **Verification Checklist**:
  - Correct number of rows selected (as specified by user)
  - All rows highlighted in blue/gray
  - Copy operation shows marching ants border
  - "Insert copied rows above" used (not regular paste)
  - Date in A1 updated to yesterday's date
  - Format maintained: M/D-M/D/YYYY

## Automation Context

This skill is designed for:
- Daily MTD tracking updates
- Monthly period transitions
- Automated report generation workflows
- Multi-partner campaign performance monitoring

## Integration Points

This automation works with campaign data from partners including:
- Samsung, PerforMarkt, Pointblank, AdsPostX
- True Finance, T-Mobile, Thanks.co
- Platforms: Android, iOS, Web, TV Universal

## Detailed Troubleshooting Guide

### Problem: Copy/Insert Operation Fails

**Symptom**: Data gets overwritten or paste doesn't work correctly

**Root Cause**: Using regular paste (Ctrl+V) instead of "Insert copied rows above"

**Solution**:
1. ALWAYS select entire ROWS (click row numbers 1-17, not cells)
2. Copy with Ctrl+C (verify marching ants appear)
3. Right-click on row number 1 (NOT on a cell)
4. Select "Insert 17 copied rows above" from menu
5. This inserts AND pastes in one operation - existing data shifts down

**What NOT to do**:
- ❌ Don't select cells (like A1:E17) - select ROWS
- ❌ Don't use regular paste (Ctrl+V) - use "Insert copied rows"
- ❌ Don't right-click on cells - right-click on row NUMBERS

### Problem: "Insert Copied Rows" Option Not Showing

**Symptom**: Context menu doesn't show "Insert X copied rows above"

**Root Cause**: Copied cells instead of rows, or didn't copy at all

**Solution**:
1. Verify you copied ROWS: Click row number 1, Shift+Click row 17
2. Press Ctrl+C and confirm marching ants border appears
3. Right-click on the row NUMBER (gray area on left), not on cells
4. The option should appear as "Insert 17 copied rows above"

### Problem: Formatting Lost After Paste

**Symptom**: Colors, borders, or fonts don't match original

**Root Cause**: Selected and copied cells instead of entire rows

**Solution**:
- Always click on ROW NUMBERS (left gray area) to select entire rows
- This preserves all formatting, column widths, and styling
- Never select just cells (like A1:E17) when you need to preserve formatting

### Problem: Data Overwritten Instead of Inserted

**Symptom**: Original data at row 1 was replaced, not shifted down

**Root Cause**: Used paste (Ctrl+V) without inserting rows first

**Solution**:
- Use "Insert copied rows above" - this is ONE operation that inserts AND pastes
- If you must use two-step method:
  1. First: Insert X empty rows at top
  2. Then: Paste with Ctrl+V
- Never paste directly without inserting rows first

### Problem: Unsure How Many Rows to Copy

**Symptom**: Don't know the current block size

**Solutions**:
1. Look at the sheet - find where the next date range pattern appears in column A
2. Count the rows from row 1 to the row before the next date pattern
3. Typical sizes: 15-25 rows depending on number of campaigns
4. You can always check the sheet visually to count the data block

### Quick Verification Checklist

Before considering operation complete:
- [ ] Asked user for number of rows to copy
- [ ] Selected ROWS (not cells) - row numbers highlighted
- [ ] Copy shows marching ants border
- [ ] Right-clicked on ROW NUMBER (not cells)
- [ ] Used "Insert copied rows above" option
- [ ] New block appears at top (rows 1-X where X is user-provided row count)
- [ ] Original block moved down (starts at row X+1)
- [ ] All formatting preserved (colors, borders)
- [ ] Date in A1 updated correctly to yesterday's date
- [ ] No data loss or overwriting occurred
