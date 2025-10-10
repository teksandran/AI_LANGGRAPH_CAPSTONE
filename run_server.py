"""
Wrapper script to run api_server.py with correct Python and dependencies check
"""
import sys
import subprocess

print("=" * 60)
print("Multi-Agent API Server - Dependency Check")
print("=" * 60)

# Check Python version
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}\n")

# Required packages
required_packages = [
    'flask',
    'flask_cors',
    'langchain',
    'langgraph',
    'langsmith',
    'dotenv'
]

missing = []
print("Checking dependencies...")
for package in required_packages:
    try:
        __import__(package.replace('_', '-'))
        print(f"  ✓ {package}")
    except ImportError:
        print(f"  ✗ {package} - MISSING")
        missing.append(package)

if missing:
    print(f"\n⚠ Missing packages: {', '.join(missing)}")
    print("\nInstalling missing packages...")

    # Map package names for pip
    pip_names = {
        'dotenv': 'python-dotenv',
        'flask_cors': 'flask-cors'
    }

    for pkg in missing:
        pip_name = pip_names.get(pkg, pkg)
        print(f"Installing {pip_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

    print("\n✓ All dependencies installed!\n")
else:
    print("\n✓ All dependencies satisfied!\n")

print("=" * 60)
print("Starting API Server...")
print("=" * 60)
print()

# Import and run api_server
try:
    import api_server
except Exception as e:
    print(f"\n❌ Error starting server: {e}")
    print("\nTroubleshooting:")
    print("1. Check .env file exists with API keys")
    print("2. Run: pip install -r requirements.txt")
    print("3. See TROUBLESHOOTING.md for help")
    sys.exit(1)
