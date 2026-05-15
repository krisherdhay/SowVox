$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

$backendCmd = "cd `"$root\backend`"; if (Test-Path .\venv\Scripts\Activate.ps1) { .\venv\Scripts\Activate.ps1 } elseif (Test-Path .\.venv\Scripts\Activate.ps1) { .\.venv\Scripts\Activate.ps1 }; uvicorn main:app --reload --port 8000"
$frontendCmd = "cd `"$root\frontend`"; npm run dev"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:5173"
