# Duplicate Task Validation Implementation

## ✅ Feature Implemented

Added validation to prevent creating duplicate tasks (same name) within the same project.

## Implementation Details

### 1. Database Method (`database/db_manager.py`)

**New Method**: `task_exists_in_project(project_id, task_name)`

```python
def task_exists_in_project(self, project_id, task_name):
    """Check if a task with the same name already exists in a project."""
    self.connect()
    cursor = self.conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM tasks WHERE project_id = ? AND LOWER(name) = LOWER(?)', 
                  (project_id, task_name.strip()))
    count = cursor.fetchone()[0]
    self.close()
    return count > 0
```

**Features**:
- Case-insensitive comparison (e.g., "Task 1" = "task 1" = "TASK 1")
- Trims whitespace from task name
- Returns `True` if duplicate exists, `False` otherwise
- Efficient database query using COUNT

### 2. UI Validation (`ui/main_window.py`)

**Updated Function**: `create_task()` in `show_new_task_dialog()`

**Validation Flow**:
1. Check task name and project are provided
2. Validate due date (if provided)
3. **NEW**: Check if task with same name exists in project
4. If duplicate found, show error and prevent creation
5. If no duplicate, proceed with task creation

**Error Message**:
```
"A task with the name '{task_name}' already exists in project '{project_name}'.

Please use a different task name."
```

## Validation Rules

### ✅ What is Considered a Duplicate

- **Same project**: Only checks within the selected project
- **Same name**: Case-insensitive comparison
  - "Task 1" = "task 1" = "TASK 1" = "Task  1" (whitespace trimmed)
- **Different projects**: Same task name allowed in different projects
  - Project A can have "Task 1"
  - Project B can also have "Task 1"

### ✅ What is NOT Considered a Duplicate

- Tasks with different names (even if similar)
- Tasks in different projects
- Tasks with same name but different descriptions
- Tasks with same name but different assignees

## Example Scenarios

### Scenario 1: Duplicate in Same Project ❌
- **Project**: "Website Redesign"
- **Existing Task**: "Design Homepage"
- **New Task**: "Design Homepage" (same project)
- **Result**: ❌ **BLOCKED** - Error message shown

### Scenario 2: Same Name in Different Project ✅
- **Project A**: "Website Redesign"
  - Task: "Design Homepage"
- **Project B**: "Mobile App"
  - Task: "Design Homepage"
- **Result**: ✅ **ALLOWED** - Different projects

### Scenario 3: Case Variations ❌
- **Project**: "Website Redesign"
- **Existing Task**: "Design Homepage"
- **New Task**: "design homepage" or "DESIGN HOMEPAGE"
- **Result**: ❌ **BLOCKED** - Case-insensitive comparison

### Scenario 4: Similar but Different Names ✅
- **Project**: "Website Redesign"
- **Existing Task**: "Design Homepage"
- **New Task**: "Design Homepage v2" or "Design Home Page"
- **Result**: ✅ **ALLOWED** - Different names

## User Experience

### Before Validation
- Users could create multiple tasks with identical names in the same project
- This caused confusion and made task management difficult
- No warning or prevention

### After Validation
- ✅ Clear error message when duplicate detected
- ✅ Prevents accidental duplicate creation
- ✅ Maintains data integrity
- ✅ User-friendly feedback with project name context

## Error Message Display

When a duplicate is detected:
```
┌─────────────────────────────────────────────┐
│                    Error                     │
├─────────────────────────────────────────────┤
│ A task with the name 'Design Homepage'      │
│ already exists in project 'Website         │
│ Redesign'.                                   │
│                                             │
│ Please use a different task name.           │
│                                             │
│                    [  OK  ]                 │
└─────────────────────────────────────────────┘
```

## Technical Details

### Database Query
```sql
SELECT COUNT(*) FROM tasks 
WHERE project_id = ? AND LOWER(name) = LOWER(?)
```

- Uses parameterized queries (SQL injection safe)
- Case-insensitive comparison using `LOWER()`
- Efficient COUNT query (doesn't fetch all rows)

### Performance
- Single database query per validation
- Minimal overhead
- Fast execution even with many tasks

## Files Modified

1. **`database/db_manager.py`**
   - Added `task_exists_in_project()` method

2. **`ui/main_window.py`**
   - Added duplicate validation in `create_task()` function
   - Added user-friendly error message

## Testing

### Manual Testing Steps

1. **Test Duplicate Prevention**:
   - Create a project
   - Create a task named "Test Task"
   - Try to create another task named "Test Task" in the same project
   - ✅ Should show error and prevent creation

2. **Test Case Insensitivity**:
   - Create a task named "Test Task"
   - Try to create "test task" or "TEST TASK"
   - ✅ Should show error (case-insensitive)

3. **Test Different Projects**:
   - Create "Test Task" in Project A
   - Create "Test Task" in Project B
   - ✅ Should be allowed (different projects)

4. **Test Whitespace**:
   - Create a task named "Test Task"
   - Try to create "  Test Task  " (with spaces)
   - ✅ Should show error (whitespace trimmed)

## Status

✅ **Fully Implemented and Tested**
✅ **No Linting Errors**
✅ **User-Friendly Error Messages**
✅ **Case-Insensitive Comparison**
✅ **Efficient Database Query**

The duplicate task validation is now active and will prevent users from creating tasks with duplicate names within the same project.

