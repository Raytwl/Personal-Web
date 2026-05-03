@echo off
echo Starting TeamAxis Application...
echo.
py main.py
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)

