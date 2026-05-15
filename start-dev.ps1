$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

$backendCmd = @"
cd `"$root\backend`"
if (-not (Test-Path .\venv\Scripts\Activate.ps1) -and -not (Test-Path .\.venv\Scripts\Activate.ps1)) {
    Write-Host 'Creating venv...' -ForegroundColor Cyan
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
} elseif (Test-Path .\venv\Scripts\Activate.ps1) {
    .\venv\Scripts\Activate.ps1
} else {
    .\.venv\Scripts\Activate.ps1
}
uvicorn main:app --reload --port 8000
"@

$frontendCmd = @"
cd `"$root\frontend`"
if (-not (Test-Path .\node_modules)) {
    Write-Host 'Installing npm packages...' -ForegroundColor Cyan
    npm install
}
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:5173"
