# LUMI Gateway - Cloudflare Tunnel Setup Script
# Run as Administrator

param(
    [string]$TunnelName = "lumi-tunnel",
    [string]$Hostname = "lumi.natalie-eiryk.com"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LUMI Gateway - Cloudflare Tunnel Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if cloudflared is installed
$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflared) {
    Write-Host "[1/6] Installing cloudflared..." -ForegroundColor Yellow
    winget install Cloudflare.cloudflared --accept-source-agreements --accept-package-agreements

    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "[1/6] cloudflared already installed" -ForegroundColor Green
}

# Check if already logged in
$configDir = "$env:USERPROFILE\.cloudflared"
if (-not (Test-Path "$configDir\cert.pem")) {
    Write-Host "[2/6] Authenticating with Cloudflare..." -ForegroundColor Yellow
    Write-Host "      A browser window will open. Log in to your Cloudflare account." -ForegroundColor Gray
    cloudflared tunnel login
} else {
    Write-Host "[2/6] Already authenticated with Cloudflare" -ForegroundColor Green
}

# Check if tunnel exists
$tunnelList = cloudflared tunnel list 2>&1 | Out-String
if ($tunnelList -match $TunnelName) {
    Write-Host "[3/6] Tunnel '$TunnelName' already exists" -ForegroundColor Green

    # Extract tunnel ID
    $tunnelInfo = cloudflared tunnel info $TunnelName 2>&1 | Out-String
    if ($tunnelInfo -match "([a-f0-9-]{36})") {
        $tunnelId = $Matches[1]
        Write-Host "      Tunnel ID: $tunnelId" -ForegroundColor Gray
    }
} else {
    Write-Host "[3/6] Creating tunnel '$TunnelName'..." -ForegroundColor Yellow
    $createOutput = cloudflared tunnel create $TunnelName 2>&1 | Out-String
    Write-Host $createOutput -ForegroundColor Gray

    if ($createOutput -match "([a-f0-9-]{36})") {
        $tunnelId = $Matches[1]
    }
}

# Route DNS
Write-Host "[4/6] Configuring DNS route..." -ForegroundColor Yellow
try {
    cloudflared tunnel route dns $TunnelName $Hostname 2>&1
    Write-Host "      Routed $Hostname -> $TunnelName" -ForegroundColor Green
} catch {
    Write-Host "      DNS route may already exist (this is OK)" -ForegroundColor Gray
}

# Create config file
Write-Host "[5/6] Creating config file..." -ForegroundColor Yellow
$configPath = "$configDir\config.yml"
$credPath = Get-ChildItem "$configDir\*.json" | Where-Object { $_.Name -match "[a-f0-9-]{36}" } | Select-Object -First 1

if ($credPath) {
    $configContent = @"
# LUMI Gateway Cloudflare Tunnel Config
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

tunnel: $tunnelId
credentials-file: $($credPath.FullName)

ingress:
  - hostname: $Hostname
    service: http://localhost:8765
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      keepAliveTimeout: 90s
      keepAliveConnections: 100
  - service: http_status:404

loglevel: info
"@

    $configContent | Out-File -FilePath $configPath -Encoding utf8
    Write-Host "      Config written to: $configPath" -ForegroundColor Green
} else {
    Write-Host "      ERROR: Could not find credentials file" -ForegroundColor Red
    exit 1
}

# Test tunnel
Write-Host "[6/6] Testing tunnel connection..." -ForegroundColor Yellow
Write-Host "      Starting tunnel in foreground mode (Ctrl+C to stop)" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Make sure Bifrost is running on port 8765" -ForegroundColor White
Write-Host "  2. Visit https://$Hostname to test" -ForegroundColor White
Write-Host "  3. Set up Cloudflare Access for MS Auth (see README.md)" -ForegroundColor White
Write-Host "  4. Install as service: cloudflared service install" -ForegroundColor White
Write-Host ""
Write-Host "Starting tunnel now..." -ForegroundColor Gray
Write-Host ""

cloudflared tunnel run $TunnelName
