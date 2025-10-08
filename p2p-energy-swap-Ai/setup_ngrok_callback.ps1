# PowerShell script to setup ngrok callback for M-Pesa integration
# Run this after starting your Flask app (python main_app.py)

Write-Host "🌞 AI Energy Trading Platform - ngrok Callback Setup" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# Function to check if Flask app is running
function Test-FlaskApp {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/status" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ Flask app is running!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "   ⚠️  Flask app is not responding properly" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "   ❌ Flask app is not running!" -ForegroundColor Red
        Write-Host "   💡 Start your Flask app first: python main_app.py" -ForegroundColor Cyan
        Write-Host "   🔄 Then run this script again" -ForegroundColor Cyan
        return $false
    }
}

# Function to start ngrok tunnel
function Start-NgrokTunnel {
    param([int]$Port = 5000)
    
    Write-Host "🚀 Starting ngrok tunnel..." -ForegroundColor Green
    Write-Host "   Exposing port $Port to public internet"
    
    try {
        # Start ngrok tunnel
        $ngrokProcess = Start-Process -FilePath "ngrok" -ArgumentList "http", $Port -PassThru -WindowStyle Minimized
        
        Write-Host "   ⏳ Waiting for tunnel to establish..." -ForegroundColor Yellow
        Start-Sleep -Seconds 8
        
        # Get tunnel information
        try {
            $tunnelInfo = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -TimeoutSec 10
            
            if ($tunnelInfo.tunnels.Count -gt 0) {
                $publicUrl = $tunnelInfo.tunnels[0].public_url
                
                # Prefer HTTPS URL if available
                foreach ($tunnel in $tunnelInfo.tunnels) {
                    if ($tunnel.public_url -like "https://*") {
                        $publicUrl = $tunnel.public_url
                        break
                    }
                }
                
                Write-Host "   ✅ Tunnel established successfully!" -ForegroundColor Green
                Write-Host "   🌐 Public URL: $publicUrl" -ForegroundColor Cyan
                Write-Host "   🔗 Local URL: http://localhost:$Port" -ForegroundColor Cyan
                
                return @{
                    "PublicUrl" = $publicUrl
                    "Process" = $ngrokProcess
                    "Success" = $true
                }
            } else {
                Write-Host "   ❌ No tunnels found" -ForegroundColor Red
                return @{ "Success" = $false; "Process" = $ngrokProcess }
            }
        } catch {
            Write-Host "   ⚠️  Could not fetch tunnel info from ngrok API" -ForegroundColor Yellow
            Write-Host "   📝 Please check ngrok status manually at http://localhost:4040" -ForegroundColor Cyan
            return @{ "Success" = $false; "Process" = $ngrokProcess }
        }
    } catch {
        Write-Host "   ❌ Error starting ngrok: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   💡 Make sure ngrok is installed and accessible from command line" -ForegroundColor Cyan
        return @{ "Success" = $false }
    }
}

# Function to update .env file with callback URL
function Update-EnvCallbackUrl {
    param([string]$PublicUrl)
    
    if (-not $PublicUrl) {
        return $false
    }
    
    $callbackUrl = "$PublicUrl/api/payment/callback"
    $validationUrl = "$PublicUrl/api/payment/validation"
    
    Write-Host ""
    Write-Host "📝 Updating environment configuration..." -ForegroundColor Green
    Write-Host "   Callback URL: $callbackUrl"
    Write-Host "   Validation URL: $validationUrl"
    
    $envPath = ".env"
    $envLines = @()
    
    # Read existing .env file
    if (Test-Path $envPath) {
        $envLines = Get-Content $envPath
    } else {
        Write-Host "   ⚠️  .env file not found, creating new one..." -ForegroundColor Yellow
    }
    
    # Update or add callback URLs
    $callbackUpdated = $false
    $validationUpdated = $false
    
    for ($i = 0; $i -lt $envLines.Count; $i++) {
        if ($envLines[$i] -like "PAYMENT_CALLBACK_URL=*") {
            $envLines[$i] = "PAYMENT_CALLBACK_URL=$callbackUrl"
            $callbackUpdated = $true
        } elseif ($envLines[$i] -like "PAYMENT_VALIDATION_URL=*") {
            $envLines[$i] = "PAYMENT_VALIDATION_URL=$validationUrl"
            $validationUpdated = $true
        }
    }
    
    # Add new lines if not found
    if (-not $callbackUpdated) {
        $envLines += "PAYMENT_CALLBACK_URL=$callbackUrl"
    }
    if (-not $validationUpdated) {
        $envLines += "PAYMENT_VALIDATION_URL=$validationUrl"
    }
    
    # Write back to .env file
    try {
        $envLines | Set-Content -Path $envPath
        Write-Host "   ✅ Environment file updated successfully!" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "   ❌ Failed to update .env file: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to test callback endpoint
function Test-CallbackEndpoint {
    param([string]$PublicUrl)
    
    if (-not $PublicUrl) {
        return $false
    }
    
    $callbackUrl = "$PublicUrl/api/payment/callback"
    
    Write-Host ""
    Write-Host "🧪 Testing callback endpoint..." -ForegroundColor Green
    Write-Host "   Testing: $callbackUrl"
    
    try {
        $testData = @{
            Body = @{
                stkCallback = @{
                    MerchantRequestID = "test_request_id"
                    CheckoutRequestID = "test_checkout_id"
                    ResultCode = 0
                    ResultDesc = "Test callback"
                }
            }
        } | ConvertTo-Json -Depth 3
        
        $response = Invoke-WebRequest -Uri $callbackUrl -Method POST -Body $testData -ContentType "application/json" -TimeoutSec 10 -UseBasicParsing
        
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ Callback endpoint is accessible!" -ForegroundColor Green
            Write-Host "   📊 Response: $($response.StatusCode)"
            return $true
        } else {
            Write-Host "   ⚠️  Callback endpoint returned: $($response.StatusCode)" -ForegroundColor Yellow
            return $true
        }
    } catch {
        Write-Host "   ❌ Callback endpoint not accessible: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   💡 Make sure your Flask app is running on the specified port" -ForegroundColor Cyan
        return $false
    }
}

# Function to display integration information
function Show-IntegrationInfo {
    param([string]$PublicUrl)
    
    if (-not $PublicUrl) {
        return
    }
    
    $callbackUrl = "$PublicUrl/api/payment/callback"
    $validationUrl = "$PublicUrl/api/payment/validation"
    
    Write-Host ""
    Write-Host "🔧 M-Pesa Daraja API Configuration" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "📍 Use these URLs in your M-Pesa app configuration:" -ForegroundColor Cyan
    Write-Host "   Callback URL:    $callbackUrl"
    Write-Host "   Validation URL:  $validationUrl"
    Write-Host ""
    Write-Host "🌐 ngrok Web Interface: http://localhost:4040" -ForegroundColor Cyan
    Write-Host "   - View request logs"
    Write-Host "   - Monitor callback traffic"
    Write-Host "   - Inspect HTTP requests"
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Green
    Write-Host "   1. Keep this PowerShell window open to maintain the tunnel"
    Write-Host "   2. Update your M-Pesa app with the callback URLs above"
    Write-Host "   3. Test M-Pesa STK Push with: python simple_mpesa_test.py"
    Write-Host "   4. Monitor callbacks at http://localhost:4040"
    Write-Host ""
    Write-Host "⚠️  Important:" -ForegroundColor Yellow
    Write-Host "   - This tunnel is temporary and will close when you stop this script"
    Write-Host "   - For production, use a permanent domain"
    Write-Host "   - Keep your ngrok session active during testing"
}

# Main execution
try {
    # Check if Flask app is running
    Write-Host "🔍 Checking if Flask app is running..."
    if (-not (Test-FlaskApp)) {
        exit 1
    }
    
    # Start ngrok tunnel
    $tunnelResult = Start-NgrokTunnel -Port 5000
    
    if ($tunnelResult.Success -and $tunnelResult.PublicUrl) {
        # Update environment file
        Update-EnvCallbackUrl -PublicUrl $tunnelResult.PublicUrl
        
        # Test callback endpoint
        Test-CallbackEndpoint -PublicUrl $tunnelResult.PublicUrl
        
        # Display configuration info
        Show-IntegrationInfo -PublicUrl $tunnelResult.PublicUrl
        
        # Keep tunnel alive
        Write-Host ""
        Write-Host "🔄 Tunnel is active! Press Ctrl+C to stop..." -ForegroundColor Green
        
        try {
            while ($true) {
                Start-Sleep -Seconds 60
                # Check if tunnel is still active
                try {
                    $null = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -TimeoutSec 5
                } catch {
                    Write-Host "⚠️  ngrok tunnel may have disconnected!" -ForegroundColor Yellow
                    break
                }
            }
        } catch {
            Write-Host ""
            Write-Host "🛑 Stopping ngrok tunnel..." -ForegroundColor Yellow
            if ($tunnelResult.Process -and -not $tunnelResult.Process.HasExited) {
                $tunnelResult.Process.Kill()
            }
            Write-Host "✅ Tunnel stopped successfully!" -ForegroundColor Green
        }
    } else {
        Write-Host ""
        Write-Host "❌ Failed to establish ngrok tunnel" -ForegroundColor Red
        Write-Host "💡 Troubleshooting:" -ForegroundColor Cyan
        Write-Host "   1. Check if ngrok is installed: ngrok version"
        Write-Host "   2. Verify auth token: ngrok config check"
        Write-Host "   3. Ensure port 5000 is not in use"
        Write-Host "   4. Try manually: ngrok http 5000"
    }
} catch {
    Write-Host "❌ Script error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")