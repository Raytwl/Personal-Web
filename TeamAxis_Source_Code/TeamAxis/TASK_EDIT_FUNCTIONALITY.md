# Task Edit Functionality Implementation

## ✅ Feature Implemented

Added complete task editing functionality allowing users to modify all aspects of existing tasks.

## Implementation Details

### 1. Database Methods (`database/db_manager.py`)

#### New Method: `get_task_by_id(task_id)`
```python
def get_task_by_id(self, task_id):
    """Get a task by its ID."""
```
- Retrieves a single task by its ID
- Returns `Task` object or `None` if not found
- Used to load task data for editing

#### New Method: `update_task(task_id, name, description, assignee_id, status, priority, due_date, progress=None)`
```python
def update_task(self, task_id, name, description, assignee_id, status, priority, due_date, progress=None):
    """Update task details."""
```
- Updates all task fields
- Supports optional progress parameter
- Returns `True` on success

#### Enhanced Method: `task_exists_in_project(project_id, task_name, exclude_task_id=None)`
```python
def task_exists_in_project(self, project_id, task_name, exclude_task_id=None):
```
- Added `exclude_task_id` parameter
- When editing, excludes current task from duplicate check
- Prevents false positives when keeping the same name

### 2. UI Implementation (`ui/main_window.py`)

#### New Button: "Edit Task"
- Added orange "Edit Task" button to tasks toolbar
- Positioned between "New Task" and "Mark as Complete"
- Color: `#FF9800` (orange) to distinguish from create/delete

#### New Function: `show_edit_task_dialog()`
- Opens dialog with task details pre-filled
- Validates all inputs (same as create dialog)
- Updates task in database on save
- Refreshes all relevant views

## Features

### ✅ Editable Fields

1. **Task Name** - Can be changed (with duplicate validation)
2. **Description** - Full text editing
3. **Assignee** - Can be changed or set to "Unassigned"
4. **Status** - Can change between: pending, in_progress, completed, blocked
5. **Priority** - Can change between: low, medium, high, critical
6. **Due Date** - Can be updated or cleared
7. **Progress** - Can be set from 0-100%

### ✅ Protected Fields

- **Project** - Cannot be changed (project is locked)
  - Prevents data integrity issues
  - Task must be deleted and recreated to move to different project

### ✅ Validations

1. **Task Name Required** - Cannot be empty
2. **Duplicate Name Check** - Prevents duplicate names in same project
   - Excludes current task when checking (allows keeping same name)
   - Case-insensitive comparison
3. **Due Date Format** - Must be YYYY-MM-DD if provided
4. **Due Date Range** - Year must be 1900-2100
5. **Progress Range** - Must be 0-100
6. **Progress Type** - Must be a valid number

## User Interface

### Edit Task Dialog

```
┌─────────────────────────────────────────┐
│              Edit Task                   │
├─────────────────────────────────────────┤
│ Project: [Website Redesign] (disabled)  │
│ Task Name: [Design Homepage]            │
│ Description: [Multi-line text area]     │
│ Assignee: [John Doe (ID: 2)]            │
│ Status: [in_progress ▼]                 │
│ Priority: [high ▼]                      │
│ Due Date: [2024-12-31]                  │
│ Progress (%): [75]                      │
│                                          │
│              [Cancel]  [Update]          │
└─────────────────────────────────────────┘
```

### Toolbar Button

- **Location**: Tasks tab toolbar
- **Position**: Between "New Task" and "Mark as Complete"
- **Color**: Orange (#FF9800)
- **Text**: "Edit Task"

## Usage Flow

1. **Select Task**: Click on a task in the tasks list
2. **Click Edit**: Click "Edit Task" button in toolbar
3. **Edit Fields**: Modify any editable fields in the dialog
4. **Validate**: System validates all inputs
5. **Save**: Click "Update" to save changes
6. **Refresh**: All views automatically refresh

## Error Handling

### No Task Selected
```
┌─────────────────────────────┐
│          Warning             │
├─────────────────────────────┤
│ Please select a task to edit.│
│                              │
│            [  OK  ]          │
└─────────────────────────────┘
```

### Duplicate Name
```
┌─────────────────────────────────────────┐
│              Error                       │
├─────────────────────────────────────────┤
│ A task with the name 'Design Homepage'  │
│ already exists in project 'Website     │
│ Redesign'.                               │
│                                         │
│ Please use a different task name.       │
│                                         │
│            [  OK  ]                     │
└─────────────────────────────────────────┘
```

### Invalid Progress
```
┌─────────────────────────────┐
│          Error               │
├─────────────────────────────┤
│ Progress must be between    │
│ 0 and 100.                  │
│                              │
│            [  OK  ]          │
└─────────────────────────────┘
```

## Technical Details

### Database Update Query
```sql
UPDATE tasks SET 
    name = ?, 
    description = ?, 
    assignee_id = ?, 
    status = ?, 
    priority = ?, 
    due_date = ?, 
    progress = ? 
WHERE task_id = ?
```

### Duplicate Check (When Editing)
```sql
SELECT COUNT(*) FROM tasks 
WHERE project_id = ? 
AND LOWER(name) = LOWER(?) 
AND task_id != ?
```

- Excludes current task from duplicate check
- Allows keeping the same name when editing other fields

## Auto-Refresh

After successful update, the following views are automatically refreshed:
- ✅ Tasks list
- ✅ Projects list (progress may have changed)
- ✅ Dashboard
- ✅ Project combo (for visualization)
- ✅ Visualization charts

## Example Scenarios

### Scenario 1: Edit Task Name
- **Original**: "Design Homepage"
- **Edit to**: "Design Homepage v2"
- **Result**: ✅ Updated successfully

### Scenario 2: Change Status
- **Original**: Status = "pending"
- **Edit to**: Status = "in_progress", Progress = 50%
- **Result**: ✅ Updated, project progress recalculated

### Scenario 3: Keep Same Name
- **Original**: "Design Homepage"
- **Edit**: Change description, keep name
- **Result**: ✅ Updated (duplicate check excludes current task)

### Scenario 4: Duplicate Name
- **Existing**: "Design Homepage" (Task ID: 1)
- **Another**: "Design Homepage" (Task ID: 2)
- **Edit Task 1**: Try to rename to "Design Homepage"
- **Result**: ❌ Blocked (Task 2 already has this name)

## Files Modified

1. **`database/db_manager.py`**
   - Added `get_task_by_id()` method
   - Added `update_task()` method
   - Enhanced `task_exists_in_project()` with exclude parameter

2. **`ui/main_window.py`**
   - Added "Edit Task" button to toolbar
   - Added `show_edit_task_dialog()` function
   - Integrated with existing validation system

## Status

✅ **Fully Implemented and Tested**
✅ **No Linting Errors**
✅ **All Validations Working**
✅ **User-Friendly Interface**
✅ **Auto-Refresh on Update**

The task editing functionality is now fully operational. Users can edit all task properties except the project assignment, with comprehensive validation and error handling.

