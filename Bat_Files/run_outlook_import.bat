@echo off
REM ============================================================================
REM Outlook Data Tape Import - Daily Runner
REM ============================================================================
REM WHAT: Automatically imports seller data from "Data Tape Import" Outlook folder
REM WHY: Processes unread emails only, marks them as read after import
REM HOW: Double-click this file to run the import
REM ============================================================================

echo.
echo ========================================
echo   Outlook Data Tape Import
echo ========================================
echo.
echo Scanning "Data Tape Import" folder...
echo Processing unread emails only...
echo.

cd /d "%~dp0..\projectalphav1"

python manage.py import_seller_data ^
    --scan-outlook ^
    --auto-create ^
    --outlook-folder "Data Tape Import" ^
    --outlook-unread-only ^
    --outlook-mark-read

echo.
echo ========================================
echo   Import Complete!
echo ========================================
echo.
pause
