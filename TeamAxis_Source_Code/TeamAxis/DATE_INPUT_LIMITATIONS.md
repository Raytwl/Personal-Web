# Date Input Limitations in TeamAxis

## Current Date Input Requirements

### Format
- **Required Format**: `YYYY-MM-DD` (e.g., `2024-01-15`)
- **Example**: `2024-12-31` ✅
- **Invalid**: `12/31/2024`, `31-12-2024`, `2024/01/15` ❌

### Where Dates Are Used

1. **Project Start Date** (Required)
   - Location: New Project dialog
   - Default: Current date (auto-filled)
   - Format: YYYY-MM-DD

2. **Project End Date** (Required)
   - Location: New Project dialog
   - Format: YYYY-MM-DD
   - **⚠️ No validation**: End date can be before start date

3. **Task Due Date** (Optional)
   - Location: New Task dialog
   - Format: YYYY-MM-DD
   - Can be left empty (None)

## Current Limitations

### ❌ Missing Validations

1. **No Format Validation**
   - The `validate_date()` function exists in `utils/helpers.py` but is **NOT being used**
   - Invalid date formats will cause database errors or incorrect storage
   - No user-friendly error messages for invalid formats

2. **No Logical Validation**
   - End date can be before start date (illogical)
   - No check if dates are in the future/past
   - No validation that dates are reasonable (e.g., not year 9999)

3. **No Range Validation**
   - Dates can be any value that matches YYYY-MM-DD format
   - No minimum/maximum date constraints
   - No validation against impossible dates (e.g., February 30)

4. **Error Handling**
   - Database errors may occur if invalid dates are entered
   - Error messages may not be user-friendly

### ✅ What Works

1. **Format Display**: UI labels show "YYYY-MM-DD" format
2. **Default Values**: Start date defaults to today
3. **Optional Fields**: Task due dates can be empty
4. **Date Parsing**: System can parse valid YYYY-MM-DD dates

## Recommendations for Improvement

### 1. Add Format Validation
```python
from utils.helpers import validate_date

if not validate_date(start_date):
    messagebox.showerror("Error", "Start date must be in YYYY-MM-DD format")
    return
```

### 2. Add Logical Validation
```python
# Check end date is after start date
if end_date and start_date:
    if datetime.strptime(end_date, '%Y-%m-%d') < datetime.strptime(start_date, '%Y-%m-%d'):
        messagebox.showerror("Error", "End date must be after start date")
        return
```

### 3. Add Date Range Validation
```python
# Check dates are reasonable (e.g., between 1900 and 2100)
year = int(start_date.split('-')[0])
if year < 1900 or year > 2100:
    messagebox.showerror("Error", "Date year must be between 1900 and 2100")
    return
```

## Current Behavior

### What Happens with Invalid Dates?

1. **Invalid Format** (e.g., "12/31/2024"):
   - May be stored as-is in database
   - Will cause errors when trying to parse for calculations
   - Risk warning system may fail when analyzing dates

2. **Illogical Dates** (e.g., end before start):
   - Will be accepted and stored
   - No warning or error
   - May cause confusion in reports

3. **Impossible Dates** (e.g., "2024-02-30"):
   - Python's `datetime.strptime()` will raise ValueError
   - Will cause exception when risk system tries to analyze
   - Error may not be user-friendly

## Summary

**Current State**: 
- ✅ Format requirement: YYYY-MM-DD
- ❌ No validation before saving
- ❌ No logical constraints
- ❌ No user-friendly error messages

**Risk Level**: **Medium**
- Users can enter invalid dates that cause errors
- No protection against data entry mistakes
- System may crash or behave unexpectedly with invalid dates

