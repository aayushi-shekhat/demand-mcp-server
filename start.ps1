# start.ps1 — Launch demand-mcp-server + MCP Inspector
# Usage: .\start.ps1

$PORT       = 8000
$SSE_URL    = "http://localhost:$PORT/sse"
$SCRIPT_DIR = $PSScriptRoot
$PYTHON     = "C:\Users\aayush163777\AppData\Local\Python\bin\python.exe"

# ── 1. Kill anything already holding port 8000 ─────────────────────────────
Write-Host "Checking for existing process on port $PORT..." -ForegroundColor Cyan
$existing = netstat -ano | Select-String ":$PORT\s" | Select-String "LISTENING"
if ($existing) {
    $pid_val = ($existing.ToString().Trim() -split '\s+')[-1]
    if ($pid_val -match '^\d+$') {
        Write-Host "Killing process $pid_val on port $PORT..." -ForegroundColor Yellow
        Stop-Process -Id ([int]$pid_val) -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

# ── 2. Verify Python path ──────────────────────────────────────────────────
if (-not (Test-Path $PYTHON)) {
    Write-Host "ERROR: Python not found at $PYTHON" -ForegroundColor Red
    exit 1
}
Write-Host "Python: $PYTHON" -ForegroundColor DarkGray

# ── 3. Start demand-mcp-server as a background job ────────────────────────
Write-Host "Starting demand-mcp-server on port $PORT..." -ForegroundColor Cyan
$job = Start-Job -ScriptBlock {
    param($python, $dir, $port)
    Set-Location $dir
    & $python -m uvicorn main:app --host 0.0.0.0 --port $port 2>&1
} -ArgumentList $PYTHON, $SCRIPT_DIR, $PORT

Write-Host "Server Job ID: $($job.Id)" -ForegroundColor Green

# ── 4. Wait until server is reachable (up to 20s) ─────────────────────────
Write-Host "Waiting for server to be ready..." -ForegroundColor Cyan
$ready = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Seconds 1

    # Print any new server output to help diagnose
    $out = Receive-Job -Job $job 2>&1
    if ($out) { Write-Host "[server] $out" -ForegroundColor DarkGray }

    # Use TCP test instead of HTTP to avoid security prompts in non-interactive shells
    $conn = Test-NetConnection -ComputerName "localhost" -Port $PORT -InformationLevel Quiet -WarningAction SilentlyContinue 2>$null
    if ($conn) { $ready = $true; break }
}

if (-not $ready) {
    Write-Host "Server did not start in time. Server output:" -ForegroundColor Red
    Receive-Job -Job $job 2>&1 | ForEach-Object { Write-Host "  $_" }
    Stop-Job -Job $job
    Remove-Job -Job $job
    exit 1
}
Write-Host "Server is ready at http://localhost:$PORT" -ForegroundColor Green

# ── 5. Launch MCP Inspector pointed at our SSE endpoint ───────────────────
Write-Host ""
Write-Host "Launching MCP Inspector -> $SSE_URL" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to exit (server job $($job.Id) will keep running)." -ForegroundColor DarkGray
Write-Host ""

npx @modelcontextprotocol/inspector --transport sse --server-url $SSE_URL

# ── Cleanup on exit ────────────────────────────────────────────────────────
Write-Host "Stopping server job..." -ForegroundColor Yellow
Stop-Job -Job $job -ErrorAction SilentlyContinue
Remove-Job -Job $job -ErrorAction SilentlyContinue
