# PowerShell Script to Download and Setup Ngrok for M-Pesa Testing
# Run this script to automatically download and configure ngrok

Write-Host "🚀 M-Pesa STK Push - Ngrok Setup Script" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Check if ngrok is already installed
try {
    $ngrokVersion = & ngrok version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Ngrok is already installed: $ngrokVersion" -ForegroundColor Green
    } else {
        throw "Ngrok not found"
    }
} catch {
    Write-Host "📥 Downloading and installing ngrok..." -ForegroundColor Yellow
    
    # Create temp directory
    $tempDir = New-Item -ItemType Directory -Path (Join-Path $env:TEMP "ngrok_setup") -Force
    
    # Download ngrok
    $ngrokUrl = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
    $zipPath = Join-Path $tempDir "ngrok.zip"
    
    try {
        Write-Host "⬇️  Downloading ngrok from $ngrokUrl" -ForegroundColor Yellow
        Invoke-WebRequest -Uri $ngrokUrl -OutFile $zipPath -UseBasicParsing
        
        # Extract ngrok
        Write-Host "📦 Extracting ngrok..." -ForegroundColor Yellow
        Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
        
        # Copy to current directory
        $ngrokExe = Join-Path $tempDir "ngrok.exe"
        $currentDir = Get-Location
        Copy-Item $ngrokExe -Destination $currentDir -Force
        
        Write-Host "✅ Ngrok installed to current directory" -ForegroundColor Green
        
        # Clean up
        Remove-Item $tempDir -Recurse -Force
        
    } catch {
        Write-Host "❌ Failed to download ngrok: $_" -ForegroundColor Red
        Write-Host "💡 Please download manually from: https://ngrok.com/download" -ForegroundColor Yellow
        exit 1
    }
}

# Configure ngrok with API token
Write-Host "🔑 Configuring ngrok with API token..." -ForegroundColor Yellow
$apiToken = "333FNwRH7Cp4svFWQ2DuC8HrjBf_6qXXv6viYbGFy7P4tvjbr"

try {
    & .\ngrok.exe config add-authtoken $apiToken
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Ngrok configured successfully!" -ForegroundColor Green
    } else {
        throw "Configuration failed"
    }
} catch {
    Write-Host "❌ Failed to configure ngrok" -ForegroundColor Red
    exit 1
}

# Start ngrok tunnel
Write-Host "🚀 Starting ngrok tunnel on port 5000..." -ForegroundColor Yellow
Write-Host "⚠️  Keep this window open to maintain the tunnel!" -ForegroundColor Yellow
Write-Host ""

# Start ngrok and capture output
Start-Process -FilePath ".\ngrok.exe" -ArgumentList "http", "5000", "--log=stdout" -WindowStyle Normal

# Wait for ngrok to start
Start-Sleep -Seconds 3

# Get tunnel URL
try {
    $tunnelInfo = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method Get -ErrorAction SilentlyContinue
    $httpsUrl = ($tunnelInfo.tunnels | Where-Object { $_.proto -eq "https" }).public_url
    
    if ($httpsUrl) {
        Write-Host "🎉 Ngrok tunnel is running!" -ForegroundColor Green
        Write-Host "📡 Public URL: $httpsUrl" -ForegroundColor Cyan
        Write-Host "🔄 Local URL: http://localhost:5000" -ForegroundColor Cyan
        
        # Update .env file
        $callbackUrl = "$httpsUrl/api/payment/callback"
        $envFile = ".\.env"
        
        if (Test-Path $envFile) {
            $envContent = Get-Content $envFile
            $callbackExists = $envContent | Where-Object { $_ -match "^PAYMENT_CALLBACK_URL=" }
            
            if ($callbackExists) {
                # Update existing line
                $envContent = $envContent | ForEach-Object {
                    if ($_ -match "^PAYMENT_CALLBACK_URL=") {
                        "PAYMENT_CALLBACK_URL=$callbackUrl"
                    } else {
                        $_
                    }
                }
            } else {
                # Add new line
                $envContent += ""
                $envContent += "# Ngrok Callback URL"
                $envContent += "PAYMENT_CALLBACK_URL=$callbackUrl"
            }
            
            $envContent | Set-Content $envFile
            Write-Host "✅ Updated .env with callback URL" -ForegroundColor Green
        }
        
        Write-Host ""
        Write-Host "📋 Next Steps:" -ForegroundColor Yellow
        Write-Host "1. ✅ Ngrok tunnel is running" -ForegroundColor White
        Write-Host "2. ✅ Callback URL updated in .env" -ForegroundColor White
        Write-Host "3. 🔄 Start your Flask app: python main_app.py" -ForegroundColor White
        Write-Host "4. 🔄 Test STK Push: python test_stk_push_integration.py" -ForegroundColor White
        Write-Host ""
        Write-Host "🌐 Test URLs:" -ForegroundColor Yellow
        Write-Host "   Public API: $httpsUrl/api/status" -ForegroundColor Cyan
        Write-Host "   Callback: $httpsUrl/api/payment/callback" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🚨 IMPORTANT: Keep this PowerShell window open to maintain the tunnel!" -ForegroundColor Red
        
    } else {
        Write-Host "❌ Could not retrieve tunnel URL" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Error getting tunnel information: $_" -ForegroundColor Red
    Write-Host "💡 Check if ngrok started properly" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press Enter to continue monitoring or Ctrl+C to stop..." -ForegroundColor Yellow
Read-Host