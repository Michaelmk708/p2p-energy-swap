#!/usr/bin/env python3
"""
Setup script for AI Energy Trading System
Handles installation and initial configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🌞 {text}")
    print("="*60)

def print_step(step, text):
    """Print a formatted step"""
    print(f"\n[{step}] {text}")

def run_command(command, description):
    """Run a command and handle errors"""
    try:
        print(f"   Running: {command}")
        result = subprocess.run(command.split(), check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required packages"""
    print_step("2", "Installing Dependencies")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
        print("   ✅ pip is available")
    except subprocess.CalledProcessError:
        print("   ❌ pip is not available")
        return False
    
    # Install requirements
    if os.path.exists("requirements.txt"):
        success = run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                            "Installing dependencies")
        if not success:
            print("   ⚠️ Some dependencies may have failed to install")
            print("   Try running: pip install -r requirements.txt manually")
    else:
        print("   ❌ requirements.txt not found")
        return False
    
    return True

def setup_environment():
    """Set up environment configuration"""
    print_step("3", "Setting up Environment Configuration")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists():
        if not env_file.exists():
            shutil.copy(env_example, env_file)
            print("   ✅ Created .env file from template")
        else:
            print("   ⚠️ .env file already exists, skipping")
    else:
        print("   ❌ .env.example not found")
        return False
    
    print("\n   📝 Configuration Notes:")
    print("   - Edit .env file to add your API keys")
    print("   - OpenWeatherMap API: https://openweathermap.org/api")
    print("   - Google Gemini AI: https://ai.google.dev/")
    print("   - System works with demo data if no keys provided")
    
    return True

def create_directories():
    """Create necessary directories"""
    print_step("4", "Creating Directories")
    
    directories = [
        "logs",
        "models",
        "data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ Created directory: {directory}")
    
    return True

def test_installation():
    """Test the installation"""
    print_step("5", "Testing Installation")
    
    try:
        # Test imports
        print("   Testing module imports...")
        
        # Test configuration
        sys.path.append(os.getcwd())
        from config.settings import settings
        print("   ✅ Configuration module loaded")
        
        # Test database
        from src.database.db_manager import db_manager
        print("   ✅ Database module loaded")
        
        # Test weather API
        from src.weather.weather_api import weather_service
        print("   ✅ Weather API module loaded")
        
        # Test IoT simulation
        from src.iot.smart_meter import iot_network
        print("   ✅ IoT simulation module loaded")
        
        # Test AI model
        from src.ai_models.gemini_advisor import gemini_advisor
        print("   ✅ AI model module loaded")
        
        print("\n   🔧 Running system check...")
        
        # Test weather service
        try:
            weather_data = weather_service.get_current_weather()
            print("   ✅ Weather service working")
        except Exception as e:
            print(f"   ⚠️ Weather service issue: {e}")
        
        # Test database
        try:
            db_manager.get_recent_energy_data(1)
            print("   ✅ Database working")
        except Exception as e:
            print(f"   ⚠️ Database issue: {e}")
        
        # Test IoT network
        try:
            weather_data = {'temperature': 25, 'sunlight_hours': 8, 'cloud_percentage': 30}
            network_data = iot_network.get_network_data(weather_data)
            print("   ✅ IoT network working")
        except Exception as e:
            print(f"   ⚠️ IoT network issue: {e}")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        return False

def main():
    """Main setup function"""
    print_header("AI Energy Trading System Setup v2.0")
    
    print("This script will set up the AI Energy Trading System on your machine.")
    print("Make sure you have Python 3.8+ and internet connection.")
    
    # Step 1: Check Python version
    print_step("1", "Checking Python Version")
    if not check_python_version():
        return False
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed")
        return False
    
    # Step 3: Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed")
        return False
    
    # Step 4: Create directories
    if not create_directories():
        print("\n❌ Directory creation failed")
        return False
    
    # Step 5: Test installation
    if not test_installation():
        print("\n⚠️ Installation test had issues (system may still work)")
    
    # Success message
    print_header("Setup Complete!")
    print("🎉 AI Energy Trading System is ready to use!")
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your API keys (optional)")
    print("2. Run: python main_app.py")
    print("3. Open: http://localhost:5000")
    print("4. Test API: curl http://localhost:5000/api/predict")
    
    print("\n📚 Documentation:")
    print("- README.md - Complete documentation")
    print("- .env.example - Configuration template")
    print("- logs/energy_trading.log - System logs")
    
    print("\n🔧 Troubleshooting:")
    print("- Check logs for detailed error messages")
    print("- Verify API keys in .env file")
    print("- Test with: curl http://localhost:5000/api/status")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)
    else:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)