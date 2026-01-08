---
name: create-chime-mtd-performance
description: Implementation guide for the automated MTD Performance data block workflow
---

# Implementation Guide: Create Chime MTD Performance

## Pseudo-Code Workflow

```
FUNCTION automateChimeMTDBlock():
  
  // STEP 1: Initialize and Access Sheet
  tab = openNewBrowserTab()
  navigateToURL(sheetURL)
  waitForSheetToLoad()
  
  // STEP 2: Ask User for Block Size
  // CRITICAL: The most recent block ALWAYS starts at row 1
  // Instead of complex detection, ask user directly
  PRINT "How many rows should I copy? (e.g., 17, 20, 25)"
  blockHeight = getUserInput()

  IF blockHeight <= 0:
    RETURN error("Invalid row count provided")

  // Define block boundaries based on user input
  blockStartRow = 1                            // Always row 1
  blockEndRow = blockHeight                    // User-specified row count
  
  // STEP 3: Select and Copy the Data Block
  // Select entire rows (not just cells) for better formatting preservation
  selectRows(startRow=blockStartRow, endRow=blockEndRow)
  // blockStartRow is always 1, blockEndRow is user-specified (e.g., 17)

  copySelection()
  // Verify: Clipboard should contain the selected rows

  // STEP 4: Insert Copied Rows at Top (CRITICAL STEP)
  // Method 1 (Recommended): Use "Insert copied rows above" feature
  rightClickOnRow(rowNumber=1)
  selectContextMenuOption("Insert X copied rows above")
  // This automatically inserts AND pastes in one operation
  // All existing content shifts down by blockHeight rows

  // Method 2 (Alternative): Manual insert then paste
  // insertRows(rowPosition=1, numberOfRows=blockHeight)
  // navigateToCell(A1)
  // pasteData()

  // STEP 5: Update Date Range in A1
  headerCell = getCell(A1)
  headerCell.clear()                               // Delete existing data
  newDateRange = calculateMTDDateRange(yesterday)   // Calculate new date range
  headerCell.setValue(newDateRange)                 // Write new date range

  // STEP 6: Save Sheet
  saveSheet()

  RETURN success("MTD block created and updated successfully")

END FUNCTION


// ============================================
// HELPER FUNCTIONS
// ============================================

FUNCTION getUserInput():
  /*
    Prompts the user to provide the number of rows to copy.
    Returns: Integer representing the number of rows in the data block
  */

  DISPLAY "How many rows should I copy from the top?"
  DISPLAY "Typical sizes: 15-25 rows depending on campaign count"
  DISPLAY "Example: If your data block has 17 rows, enter: 17"

  userInput = READ_INPUT()

  // Validate input
  IF userInput is not a valid integer OR userInput <= 0:
    RETURN error("Please provide a valid positive number")
  END IF

  RETURN userInput

END FUNCTION


FUNCTION calculateMTDDateRange(yesterdayDate):
  /*
    Calculates the MTD (Month-to-Date) date range based on yesterday's date.
    Start date is always the 1st of yesterday's month.
    End date is yesterday's date.

    Format: M/DD-M/DD/YYYY (no spaces)

    Examples:
    - Yesterday: Jan 10, 2026 → "1/01-1/10/2026"
    - Yesterday: Jan 1, 2025 → "1/01-1/01/2025"
    - Yesterday: Feb 2, 2026 → "2/01-2/02/2026"
    - Yesterday: Dec 31, 2025 → "12/01-12/31/2025"
  */

  // Extract components from yesterday's date
  year = yesterdayDate.getFullYear()
  month = yesterdayDate.getMonth() + 1          // JavaScript months are 0-indexed
  day = yesterdayDate.getDate()

  // Start date is always the 1st of the month
  startMonth = month
  startDay = "01"

  // End date is yesterday
  endMonth = month
  endDay = padWithZero(day)                     // Ensure 2-digit format (01, 02, etc.)

  // Construct date range string: M/DD-M/DD/YYYY
  dateRange = startMonth + "/" + startDay + "-" + endMonth + "/" + endDay + "/" + year

  RETURN dateRange

END FUNCTION


// ============================================
// UTILITY FUNCTIONS
// ============================================


FUNCTION padWithZero(number):
  /*
    Pads a number with leading zero if it's single digit
    Examples: 1 → "01", 10 → "10", 5 → "05"
  */
  IF number < 10:
    RETURN "0" + number
  ELSE:
    RETURN string(number)
  END IF
END FUNCTION
```

## Implementation Steps for Browser Automation

### Using Claude in Chrome Extension

1. **Open New Tab**
   - Execute: Click "+" button to open new tab
   - Verify: New blank tab appears

2. **Navigate to Sheet**
   - Execute: Paste URL into address bar
   - Verify: Google Sheets loads with the target spreadsheet
   - Wait: Sheet data fully loads (may take 2-3 seconds)

3. **Ask User for Block Size**
   - Execute: Display prompt "How many rows should I copy? (e.g., 17, 20, 25)"
   - Wait: User provides row count
   - Validate: Ensure input is a positive integer
   - Record: User-specified row count (e.g., 17)

4. **Select Entire Rows (Not Just Cells)**
   - Execute: Click on row number 1 (left side gray area with row numbers)
   - Hold Shift and click on end row number (e.g., row 17)
   - Alternative: Click row 1, then Shift+Click row 17
   - Verify: Entire rows 1-17 are highlighted (blue/gray background)
   - **Critical**: Select ROWS not cells - this preserves all formatting

5. **Copy Selected Rows**
   - Execute: Ctrl+C (Windows/Linux) or Cmd+C (Mac)
   - Alternative: Right-click on selected rows → "Copy"
   - Verify: Moving dotted border appears around selected rows (marching ants animation)

6. **Insert Copied Rows at Top (CRITICAL OPERATION)**
   - **Method 1 (Recommended - One-Step Operation):**
     - Right-click on row number 1
     - Select: "Insert X copied rows above" where X = number of copied rows
     - This inserts AND pastes in one operation
     - Verify: New rows appear at top with copied data

   - **Method 2 (Two-Step Alternative):**
     - Right-click on row number 1
     - Select: "Insert X rows above" to create empty rows
     - Click cell A1
     - Press Ctrl+V (or Cmd+V) to paste
     - Verify: Data appears in new rows

7. **Verify Insertion Success**
   - Check: New block appears at rows 1-17 (or user-specified row count)
   - Check: Original first block now starts at row 18 (= blockHeight + 1)
   - Check: All data intact, no overwrites
   - Check: Formatting preserved (colors, borders, fonts)

8. **Update Date Range in A1**
   - Execute: Click on cell A1 to select it
   - Execute: Press Delete or Backspace to clear existing data
   - Calculate the new date range:
     - Yesterday: If today is 1/8/2026, yesterday is 1/7/2026
     - Start date: 1st of yesterday's month = 1/01
     - End date: Yesterday's date = 1/07
     - Format: M/DD-M/DD/YYYY (no spaces)
   - Execute: Type the new date range: "1/01-1/07/2026"
   - Execute: Press Enter to save
   - Verify: A1 shows the new date range in correct format

9. **Save and Verify Complete Operation**
    - Execute: Google Sheets auto-saves (wait for "Saved to Drive" message)
    - OR press Ctrl+S / Cmd+S if needed
    - Final verification checklist:
      - [ ] New block at rows 1-17 with updated date in A1
      - [ ] Original block now at rows 18-34
      - [ ] Second original block at rows 35+
      - [ ] All data present, no loss
      - [ ] Formatting preserved
      - [ ] Sheet saved successfully

## Key Data Points to Track

When implementing, track these variables:

```
blockStartRow = ALWAYS 1 (most recent block starts at row 1)
blockEndRow = user-provided row count (e.g., 17)
blockHeight = blockEndRow (same as user input)
headerText = the full text in cell A1 before update
yesterday = today's date - 1 day
newEndDate = formatted yesterday's date (M/D format)
```

## Error Handling

Handle these scenarios:

1. **Invalid User Input for Row Count**
   - Action: Re-prompt with clear instructions
   - Message: "Please provide a valid positive number (e.g., 17, 20, 25)"
   - Note: Ensure input is an integer greater than 0

2. **User Unsure of Row Count**
   - Action: Provide guidance on how to find the row count
   - Message: "Look at column A and find where the next date range pattern appears. Count rows from 1 to that row minus 1."
   - Note: Typical sizes are 15-25 rows

3. **Date Format Mismatch**
   - Action: Analyze existing date format and match it
   - Message: "Adapting date format to match existing data"

4. **Sheet Not Accessible**
   - Action: Verify permissions and retry
   - Message: "Unable to access sheet, check permissions"

5. **Copy/Paste Failure**
   - Action: Retry operation
   - Message: "Operation failed, retrying..."

## Verification Checklist

Before completing, verify:

- [ ] User provided valid row count
- [ ] New block appears at row 1
- [ ] All data from original block is present (no missing rows/columns)
- [ ] Previous row 1 is now at row (blockHeight + 1)
- [ ] Cell A1 contains updated header with yesterday's date
- [ ] Date format in A1 matches format of existing blocks
- [ ] No data loss or overwrites occurred
- [ ] Sheet is saved successfully
