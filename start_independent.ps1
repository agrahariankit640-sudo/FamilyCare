$workingDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $workingDir) { $workingDir = "c:\Users\radhe\OneDrive\Documents\FamilyCare" }
Set-Location $workingDir

# Stop existing processes on port 5000
$connections = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($connections) {
    foreach ($c in $connections) {
        Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

# Stop any existing cloudflared
Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 1

# Start python app hidden
Start-Process -FilePath "$workingDir\venv\Scripts\python.exe" -ArgumentList "app.py" -WorkingDirectory $workingDir -WindowStyle Hidden

Start-Sleep -Seconds 3

# Start cloudflared hidden logging to tunnel_public.log
$cloudflared = "$env:TEMP\cloudflared.exe"
if (Test-Path "$workingDir\tunnel_public.log") {
    Remove-Item "$workingDir\tunnel_public.log" -Force -ErrorAction SilentlyContinue
}

Start-Process -FilePath $cloudflared -ArgumentList "tunnel --url http://127.0.0.1:5000 --logfile `"$workingDir\tunnel_public.log`"" -WorkingDirectory $workingDir -WindowStyle Hidden

Start-Sleep -Seconds 6

# Read generated URL
if (Test-Path "$workingDir\tunnel_public.log") {
    $content = Get-Content "$workingDir\tunnel_public.log"
    $match = [regex]::Match($content, "https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    if ($match.Success) {
        Set-Content -Path "$workingDir\LIVE_URL.txt" -Value $match.Value
        Write-Host "Public URL is: $($match.Value)"
    }
}
