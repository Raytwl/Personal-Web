# How to Run TeamAxis Application

## Quick Start

### Option 1: Using the batch file (Windows)
Double-click `run_app.bat` or run:
```bash
run_app.bat
```

### Option 2: Using Python directly
```bash
py main.py
```

**Note:** On Windows, use `py` instead of `python` if `python` command doesn't work.

## Troubleshooting

### If you don't see the login window:

1. **Check if it's behind other windows**: The login window should appear in the center of your screen. Try Alt+Tab to switch between windows.

2. **Check the taskbar**: Look for a window titled "TeamAxis - Login" in your taskbar.

3. **Run with console output**: The application should print messages when starting. If you see errors, they will be displayed.

### If you get import errors:

Run the test script first:
```bash
py test_imports.py
```

This will verify all dependencies are correctly installed.

### If you get "python is not recognized":

Use `py` instead of `python`:
```bash
py main.py
```

## Default Login Credentials

- **Username:** admin
- **Password:** admin123
- **License Key:** (Admin users can skip the license key)

## Creating a Test License

To create a test license for regular users:
```bash
py create_test_license.py
```

This will generate a license key that you can use for registration.

## Requirements

Make sure you have installed all required packages:
```bash
py -m pip install -r requirements.txt
```

Required packages:
- matplotlib==3.8.2
- pandas==2.1.4
- numpy==1.26.2
- Pillow==10.1.0

