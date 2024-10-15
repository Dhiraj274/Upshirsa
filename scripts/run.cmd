@REM #!/bin/bash

@REM echo "Select mode:"
@REM echo "1. CLI"
@REM echo "2. Gradio UI"
@REM read -p "Enter choice [1 or 2]: " choice

@REM if [ "$choice" -eq 1 ]; then
@REM     python main.py
@REM elif [ "$choice" -eq 2 ]; then
@REM     python ui.py
@REM else
@REM     echo "Invalid choice."
@REM fi

@echo off

echo Select mode:
echo 1. CLI
echo 2. Gradio UI
set /p choice="Enter choice [1 or 2]: "

if "%choice%"=="1" (
    python main.py
) else if "%choice%"=="2" (
    python ui.py
) else (
    echo Invalid choice.
)
