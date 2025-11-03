"""
Setup Verification Script
Tests all components and API keys before running the main application.
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
from pathlib import Path

def print_status(message, status="info"):
    """Print colored status messages."""
    colors = {
        "success": "\033[92m✓",
        "error": "\033[91m✗",
        "warning": "\033[93m⚠",
        "info": "\033[94mℹ"
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')} {message}{reset}")


def verify_environment():
    """Verify Python environment and packages."""
    print("\n" + "="*70)
    print("ENVIRONMENT VERIFICATION")
    print("="*70)

    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print_status(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}", "success")
    else:
        print_status(f"Python version too old: {python_version.major}.{python_version.minor}", "error")
        return False

    # Check required packages
    required_packages = [
        "flask",
        "langchain",
        "langchain_core",
        "langchain_openai",
        "langchain_anthropic",
        "langchain_community",
        "langgraph",
        "faiss",
        "sentence_transformers",
        "beautifulsoup4",
        "httpx",
        "pydantic",
        "python-dotenv"
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_status(f"Package '{package}' installed", "success")
        except ImportError:
            print_status(f"Package '{package}' NOT installed", "error")
            missing_packages.append(package)

    if missing_packages:
        print_status(f"\nMissing packages: {', '.join(missing_packages)}", "error")
        print("\nRun: .venv\\Scripts\\pip install -r requirements.txt")
        return False

    return True


def verify_api_keys():
    """Verify API keys are configured."""
    print("\n" + "="*70)
    print("API KEY VERIFICATION")
    print("="*70)

    load_dotenv()

    # Check Yelp API Key
    yelp_key = os.getenv("YELP_API_KEY")
    if yelp_key and yelp_key != "your_yelp_key_here":
        print_status("YELP_API_KEY: Configured", "success")
        has_yelp = True
    else:
        print_status("YELP_API_KEY: NOT configured", "error")
        print("  Get your key at: https://www.yelp.com/developers")
        has_yelp = False

    # Check OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.startswith("sk-") and len(openai_key) > 20:
        print_status("OPENAI_API_KEY: Configured", "success")
        has_openai = True
    else:
        print_status("OPENAI_API_KEY: NOT configured or invalid", "warning")
        print("  Get your key at: https://platform.openai.com/api-keys")
        has_openai = False

    # Check Anthropic API Key
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key and anthropic_key != "your_anthropic_key_here" and len(anthropic_key) > 20:
        print_status("ANTHROPIC_API_KEY: Configured", "success")
        has_anthropic = True
    else:
        print_status("ANTHROPIC_API_KEY: NOT configured", "warning")
        print("  Get your key at: https://console.anthropic.com/")
        has_anthropic = False

    if not has_openai and not has_anthropic:
        print_status("\n⚠ You need at least one LLM API key (OpenAI or Anthropic)", "error")
        return False

    if not has_yelp:
        print_status("\n⚠ Yelp API key is required for business search", "error")
        return False

    return True


def test_yelp_connection():
    """Test Yelp API connection."""
    print("\n" + "="*70)
    print("YELP API CONNECTION TEST")
    print("="*70)

    try:
        import httpx

        yelp_key = os.getenv("YELP_API_KEY")
        if not yelp_key:
            print_status("Skipping - No API key configured", "warning")
            return False

        headers = {"Authorization": f"Bearer {yelp_key}"}
        url = "https://api.yelp.com/v3/businesses/search"
        params = {"location": "San Francisco", "term": "beauty", "limit": 1}

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            print_status("Yelp API connection successful", "success")
            return True
        else:
            print_status(f"Yelp API error: {response.status_code}", "error")
            print(f"  Response: {response.text[:200]}")
            return False

    except Exception as e:
        print_status(f"Connection test failed: {str(e)}", "error")
        return False


def test_llm_connection():
    """Test LLM API connection."""
    print("\n" + "="*70)
    print("LLM API CONNECTION TEST")
    print("="*70)

    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    # Test OpenAI
    if openai_key and openai_key.startswith("sk-"):
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, max_tokens=10)
            response = llm.invoke("Say 'test'")
            print_status("OpenAI API connection successful", "success")
            return True
        except Exception as e:
            print_status(f"OpenAI API error: {str(e)[:100]}", "error")
            if "401" in str(e) or "invalid" in str(e).lower():
                print("  ⚠ Your OpenAI API key is invalid or expired")
                print("  → Get a new key at: https://platform.openai.com/api-keys")

    # Test Anthropic
    if anthropic_key and anthropic_key != "your_anthropic_key_here":
        try:
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0, max_tokens=10)
            response = llm.invoke("Say 'test'")
            print_status("Anthropic API connection successful", "success")
            return True
        except Exception as e:
            print_status(f"Anthropic API error: {str(e)[:100]}", "error")

    print_status("No working LLM API key found", "error")
    print("\n📝 To fix:")
    print("  1. Get an API key from OpenAI or Anthropic")
    print("  2. Update your .env file")
    print("  3. Run this verification script again")
    return False


def verify_project_structure():
    """Verify project files and directories exist."""
    print("\n" + "="*70)
    print("PROJECT STRUCTURE VERIFICATION")
    print("="*70)

    required_paths = [
        "src/",
        "src/langgraph_agent.py",
        "src/rag_system.py",
        "src/tools.py",
        "src/yelp_client.py",
        "examples/",
        "requirements.txt",
        ".env"
    ]

    all_exist = True
    for path in required_paths:
        full_path = Path(path)
        if full_path.exists():
            print_status(f"{path}: Found", "success")
        else:
            print_status(f"{path}: NOT FOUND", "error")
            all_exist = False

    return all_exist


def main():
    """Run all verification checks."""
    print("\n" + "="*70)
    print("🔍 BEAUTY SEARCH AGENT - SETUP VERIFICATION")
    print("="*70)

    results = {
        "environment": False,
        "api_keys": False,
        "yelp": False,
        "llm": False,
        "structure": False
    }

    # Run checks
    results["structure"] = verify_project_structure()
    results["environment"] = verify_environment()
    results["api_keys"] = verify_api_keys()

    if results["api_keys"]:
        results["yelp"] = test_yelp_connection()
        results["llm"] = test_llm_connection()

    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)

    for check, passed in results.items():
        status = "success" if passed else "error"
        print_status(f"{check.upper()}: {'PASSED' if passed else 'FAILED'}", status)

    all_passed = all(results.values())

    print("\n" + "="*70)
    if all_passed:
        print_status("✓ All checks passed! You're ready to go!", "success")
        print("\n📚 Next steps:")
        print("  1. Run: .venv\\Scripts\\python examples\\enhanced_product_search.py")
        print("  2. Run: .venv\\Scripts\\python test_agent.py")
        print("  3. Run: .venv\\Scripts\\python app.py")
    else:
        print_status("✗ Some checks failed. Please fix the issues above.", "error")
        print("\n📝 Common fixes:")
        print("  • Install packages: .venv\\Scripts\\pip install -r requirements.txt")
        print("  • Update .env file with valid API keys")
        print("  • Verify you're in the project directory")
    print("="*70 + "\n")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
