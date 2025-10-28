@echo off
REM ============================================================================
REM Outlook Data Tape Import - PREVIEW MODE (Dry Run)
REM ============================================================================
REM WHAT: Preview what would be imported WITHOUT making database changes
REM WHY: Safely test before running the real import
REM HOW: Double-click this file to see what would be imported
REM ============================================================================

echo.
echo ========================================
echo   Outlook Data Tape Import - PREVIEW
echo ========================================
echo.
echo ** DRY RUN MODE - NO DATABASE CHANGES **
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
    --dry-run

echo.
echo ========================================
echo   Preview Complete!
echo   (No data was imported)
echo ========================================
echo.
echo To import for real, run: run_outlook_import.bat
echo.
pause
