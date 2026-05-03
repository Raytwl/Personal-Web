# Updated Duplicate Task Validation

## ✅ Updated Validation Rule

Tasks are now considered duplicates only when they have **BOTH**:
1. **Same name** (case-insensitive)
2. **Same due date** (or both have no due date)

## Previous vs. New Validation

### Previous Rule ❌
- Tasks were duplicates if they had the **same name** in the same project
- Due date was not considered

### New Rule ✅
- Tasks are duplicates only if they have **same name AND same due date** in the same project
- Allows multiple tasks with the same name if they have different due dates

## Implementation Details

### Database Method (`database/db_manager.py`)

**Updated Method**: `task_exists_in_project(project_id, task_name, due_date=None, exclude_task_id=None)`

```python
def task_exists_in_project(self, project_id, task_name, due_date=None, exclude_task_id=None):
    """Check if a task with the same name and due date already exists in a project."""
```

**Key Features**:
- Checks both name and due date
- Handles NULL due dates correctly (tasks with no due date match other tasks with no due date)
- Case-insensitive name comparison
- Supports excluding a task ID (for editing)

### SQL Logic

#### When Due Date is NULL/Empty:
```sql
SELECT COUNT(*) FROM tasks 
WHERE project_id = ? 
AND LOWER(name) = LOWER(?) 
AND (due_date IS NULL OR due_date = '')
```

#### When Due Date is Provided:
```sql
SELECT COUNT(*) FROM tasks 
WHERE project_id = ? 
AND LOWER(name) = LOWER(?) 
AND due_date = ?
```

## Example Scenarios

### ✅ Allowed (Not Duplicates)

1. **Same Name, Different Due Dates**
   - Task 1: "Design Homepage" - Due: 2024-12-31
   - Task 2: "Design Homepage" - Due: 2025-01-15
   - **Result**: ✅ **ALLOWED** - Different due dates

2. **Same Name, One Has Due Date, One Doesn't**
   - Task 1: "Design Homepage" - Due: 2024-12-31
   - Task 2: "Design Homepage" - Due: None
   - **Result**: ✅ **ALLOWED** - Different due date status

3. **Same Name and Due Date, Different Projects**
   - Project A: "Design Homepage" - Due: 2024-12-31
   - Project B: "Design Homepage" - Due: 2024-12-31
   - **Result**: ✅ **ALLOWED** - Different projects

### ❌ Blocked (Duplicates)

1. **Same Name and Due Date in Same Project**
   - Task 1: "Design Homepage" - Due: 2024-12-31
   - Task 2: "Design Homepage" - Due: 2024-12-31 (same project)
   - **Result**: ❌ **BLOCKED** - Exact duplicate

2. **Same Name, Both No Due Date**
   - Task 1: "Design Homepage" - Due: None
   - Task 2: "Design Homepage" - Due: None (same project)
   - **Result**: ❌ **BLOCKED** - Both have no due date

3. **Case Variations with Same Due Date**
   - Task 1: "Design Homepage" - Due: 2024-12-31
   - Task 2: "design homepage" - Due: 2024-12-31 (same project)
   - **Result**: ❌ **BLOCKED** - Case-insensitive name match + same due date

## Error Messages

### When Due Date is Provided:
```
A task with the name '{name}' and due date '{due_date}' 
already exists in project '{project_name}'.

Please use a different task name or due date.
```

### When Due Date is Not Provided:
```
A task with the name '{name}' and no due date 
already exists in project '{project_name}'.

Please use a different task name or set a due date.
```

## Use Cases

### Scenario 1: Multiple Versions with Different Deadlines
- **Use Case**: Creating multiple iterations of the same task with different deadlines
- **Example**: 
  - "Design Homepage v1" - Due: 2024-12-31
  - "Design Homepage v1" - Due: 2025-01-15
- **Result**: ✅ Allowed (different due dates)

### Scenario 2: Recurring Tasks
- **Use Case**: Same task repeated at different times
- **Example**:
  - "Weekly Review" - Due: 2024-12-15
  - "Weekly Review" - Due: 2024-12-22
  - "Weekly Review" - Due: 2024-12-29
- **Result**: ✅ Allowed (different due dates)

### Scenario 3: Exact Duplicate Prevention
- **Use Case**: Prevent accidentally creating the exact same task twice
- **Example**:
  - "Design Homepage" - Due: 2024-12-31
  - "Design Homepage" - Due: 2024-12-31 (attempt to create again)
- **Result**: ❌ Blocked (exact duplicate)

## Technical Details

### NULL Handling
- Tasks with `NULL` due date are considered to have "no due date"
- Two tasks with no due date match each other
- A task with a due date does NOT match a task with no due date

### Case Sensitivity
- Name comparison is **case-insensitive**
- "Task 1" = "task 1" = "TASK 1"
- Due date comparison is **exact** (case-sensitive for date format)

### Editing Behavior
- When editing a task, the current task is excluded from duplicate check
- Allows keeping the same name and due date when editing other fields
- Prevents false positives during editing

## Files Modified

1. **`database/db_manager.py`**
   - Updated `task_exists_in_project()` method signature
   - Added `due_date` parameter
   - Updated SQL queries to check both name and due date
   - Enhanced NULL handling for due dates

2. **`ui/main_window.py`**
   - Updated calls to `task_exists_in_project()` to pass `due_date`
   - Updated error messages to mention both name and due date
   - Added conditional error messages based on due date presence

## Status

✅ **Fully Implemented**
✅ **NULL Due Date Handling**
✅ **Case-Insensitive Name Comparison**
✅ **User-Friendly Error Messages**
✅ **Editing Support (exclude_task_id)**

The duplicate task validation now correctly checks both name and due date, allowing more flexibility while still preventing exact duplicates.

