@echo off
REM ===========================
REM Email Sync Scheduler - Runs every 10 minutes
REM ===========================

setlocal EnableDelayedExpansion

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ===========================
echo Email Sync Scheduler Started
echo Running email_sync.py every 10 minutes
echo Press Ctrl+C to stop
echo ===========================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

REM Infinite loop to run the script every 10 minutes
:loop
    echo [%date% %time%] Starting email sync...
    echo.
    
    REM Run the Python script
    call python email_sync.py
    
    echo.
    echo [%date% %time%] Script completed successfully
    
    echo.
    echo [%date% %time%] Waiting 10 minutes before next run...
    echo ===========================
    echo.
    
    REM Wait 10 minutes (600 seconds)
    timeout /t 600 /nobreak
    
    echo.
    echo ===========================
    echo.
    
    REM Go back to the beginning of the loop
goto loop
