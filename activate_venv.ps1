# PowerShell Virtual Environment Activation Script
# This script bypasses execution policy restrictions to activate the virtual environment
# Usage: . .\activate_venv.ps1  (note the dot-space before the script name for dot-sourcing)

# Get the script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPath = Join-Path $scriptPath ".venv\Scripts\Activate.ps1"

# Check if the venv activation script exists
if (Test-Path $venvPath) {
    # Temporarily bypass execution policy for this session and activate
    $originalPolicy = Get-ExecutionPolicy -Scope Process
    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
    
    try {
        # Dot-source the activation script
        . $venvPath
        Write-Host "Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green
    } catch {
        Write-Host "Error activating virtual environment: $_" -ForegroundColor Red
    } finally {
        # Restore original execution policy
        Set-ExecutionPolicy -ExecutionPolicy $originalPolicy -Scope Process -Force
    }
} else {
    Write-Host "Error: Virtual environment not found at $venvPath" -ForegroundColor Red
    Write-Host "Alternative: Use .venv\Scripts\activate.bat instead" -ForegroundColor Yellow
}
