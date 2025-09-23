@echo off
title AI Energy Trading - M-Pesa Callback Setup

echo.
echo ===================================
echo AI Energy Trading Platform
echo M-Pesa Callback Setup
echo ===================================
echo.

:: Check if Flask app is running
echo [1/3] Checking Flask application...
curl -s http://localhost:5000/api/status >nul 2>&1
if %errorlevel% neq 0 (
    echo     ❌ Flask app is not running!
    echo     💡 Please start your Flask app first:
    echo        python main_app.py
    echo.
    pause
    exit /b 1
) else (
    echo     ✅ Flask app is running!
)

echo.
echo [2/3] Starting ngrok tunnel...
echo     🚀 Exposing port 5000 to internet...

:: Start ngrok tunnel
start "" ngrok http 5000

:: Wait for tunnel to establish
echo     ⏳ Waiting for tunnel...
timeout /t 10 /nobreak >nul

:: Get tunnel URL (simplified - user will see it in ngrok window)
echo     ✅ ngrok tunnel started!
echo     🌐 Check the ngrok window for your public URL

echo.
echo [3/3] Setup Instructions:
echo     📍 Copy the HTTPS URL from the ngrok window
echo     🔧 Your callback URLs will be:
echo        - Callback: https://your-ngrok-url.ngrok.io/api/payment/callback
echo        - Validation: https://your-ngrok-url.ngrok.io/api/payment/validation
echo.
echo     📋 Next Steps:
echo        1. Keep the ngrok window open
echo        2. Update your M-Pesa app with the callback URLs
echo        3. Run: python simple_mpesa_test.py
echo        4. Monitor at: http://localhost:4040
echo.
echo     ⚠️  Important: Keep both windows open during testing!
echo.

echo 🔄 Press any key to run the Python setup script for automatic configuration...
pause >nul

:: Run the Python setup script
echo.
echo Running automated setup...
python quick_callback_setup.py

echo.
echo Setup complete! Press any key to exit...
pause >nul