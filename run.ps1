# Deforestation Dashboard - PowerShell Quick Start

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Cyan
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Please install Python 3.8+" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Check project directory
if (-not (Test-Path "requirements.txt")) {
    Write-Host "ERROR: Not in project directory" -ForegroundColor Red
    Write-Host "Please run from: C:\Users\aliscia\deforestation-dashboard\" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Deforestation Dashboard - PowerShell" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Install dependencies
Write-Host "Step 1: Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "`nStep 2: Starting servers..." -ForegroundColor Yellow
Write-Host "`nRemember:" -ForegroundColor Cyan
Write-Host "  - Backend: http://localhost:5000" -ForegroundColor Green
Write-Host "  - Frontend: http://localhost:8000" -ForegroundColor Green
Write-Host "  - Press Ctrl+C to stop servers" -ForegroundColor Green

# Start backend in background job
Write-Host "`nStarting backend server..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    cd "$env:USERPROFILE\deforestation-dashboard\backend"
    python app.py
}

# Wait for backend
Start-Sleep -Seconds 3

# Start frontend in background job
Write-Host "Starting frontend server..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    cd "$env:USERPROFILE\deforestation-dashboard\frontend"
    python app.py
}

# Wait for frontend
Start-Sleep -Seconds 2

# Open browser
Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Process "http://localhost:8000"

Write-Host "`nDashboard started!" -ForegroundColor Green
Write-Host "Browser: http://localhost:8000" -ForegroundColor Cyan
Write-Host "`nJobs running:" -ForegroundColor Cyan
Get-Job -State Running | Format-Table -Property Id, Name, State

Write-Host "`nTo stop servers, run:" -ForegroundColor Yellow
Write-Host "  Get-Job | Stop-Job" -ForegroundColor Gray

# Keep script running
Read-Host "Press Enter to continue monitoring..."

# Wait for jobs
Wait-Job -Job $backendJob, $frontendJob
