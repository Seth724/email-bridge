"""
Email Bridge - Health Check & Validation Script

Run this to verify your Email Bridge installation is configured correctly.
Does NOT consume API credits - only validates configuration.

Usage:
    python tests/health_check.py
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_python_version():
    """Check Python version"""
    print("\n" + "=" * 70)
    print("CHECKING PYTHON VERSION")
    print("=" * 70)
    
    version = sys.version_info
    version_string = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version_string} - OK")
        return True
    else:
        print(f"❌ Python {version_string} - Need Python 3.10+ ")
        return False


def check_dependencies():
    """Check required Python packages"""
    print("\n" + "=" * 70)
    print("CHECKING DEPENDENCIES")
    print("=" * 70)
    
    required_packages = [
        "dotenv",
        "groq",
        "langgraph",
        "langchain_groq",
        "imaplib2",
        "telegram",
        "fastmcp",
        "apscheduler",
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Fix with: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies installed")
    return True


def check_environment_variables():
    """Check required environment variables"""
    print("\n" + "=" * 70)
    print("CHECKING ENVIRONMENT VARIABLES")
    print("=" * 70)
    
    required_vars = {
        "GMAIL_ADDRESS": "Gmail address (e.g., user@gmail.com)",
        "GMAIL_APP_PASSWORD": "Gmail app password (16 chars)",
        "GROQ_API_KEY": "Groq API key",
        "TELEGRAM_BOT_TOKEN": "Telegram bot token",
        "TELEGRAM_CHAT_ID": "Telegram chat ID",
    }
    
    missing = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Show masked value for security
            if len(value) > 8:
                masked = value[:4] + "*" * (len(value) - 8) + value[-4:]
            else:
                masked = "*" * len(value)
            print(f"✅ {var} = {masked}")
        else:
            print(f"❌ {var} - NOT SET")
            missing.append(var)
    
    if missing:
        print(f"\n⚠️  Missing variables: {', '.join(missing)}")
        print("\nTo set up, create a .env file with:")
        for var in missing:
            print(f"  {var}=your_value_here")
        return False
    
    print("\n✅ All required variables set")
    return True


def check_env_file():
    """Check if .env file exists"""
    print("\n" + "=" * 70)
    print("CHECKING .ENV FILE")
    print("=" * 70)
    
    if os.path.exists(".env"):
        print("✅ .env file found")
        # Check if it has any content
        with open(".env") as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        
        if lines:
            print(f"✅ .env has {len(lines)} configuration lines")
            return True
        else:
            print("⚠️  .env file is empty")
            return False
    else:
        print("❌ .env file not found")
        print("\nCreate it with: cp .env.template .env")
        return False


def check_config_module():
    """Check if config module loads"""
    print("\n" + "=" * 70)
    print("CHECKING CONFIG MODULE")
    print("=" * 70)
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
        from core.config import ConfigValidator
        
        print("✅ Config module loads successfully")
        
        # Try validation
        try:
            config = ConfigValidator.validate()
            print("✅ Configuration validation passed")
            return True
        except ValueError as e:
            print(f"❌ Configuration validation failed: {str(e)[:100]}")
            return False
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False


def check_components_import():
    """Check if all core components can be imported"""
    print("\n" + "=" * 70)
    print("CHECKING CORE COMPONENTS")
    print("=" * 70)
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
    
    components = [
        ("core.gmail", "GmailFetcher"),
        ("core.classifier", "EmailClassifier"),
        ("core.telegram", "TelegramSender"),
        ("core.rules_engine", "RulesEngine"),
        ("core.time_urgency", "TimeUrgencyManager"),
        ("workflows.triage_graph", "EmailTriageWorkflow"),
    ]
    
    all_ok = True
    for module_name, class_name in components:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"❌ {module_name}.{class_name} - {e}")
            all_ok = False
    
    if all_ok:
        print("\n✅ All components load successfully")
    
    return all_ok


def check_standalone_scripts():
    """Check if standalone scripts are callable"""
    print("\n" + "=" * 70)
    print("CHECKING STANDALONE SCRIPTS")
    print("=" * 70)
    
    scripts = [
        ("standalone/bot.py", "One-time email check"),
        ("standalone/scheduler.py", "Daily scheduler"),
        ("standalone/weekly_summary.py", "Weekly summary"),
    ]
    
    all_ok = True
    for script, description in scripts:
        if os.path.exists(script):
            print(f"✅ {script} - {description}")
        else:
            print(f"❌ {script} - NOT FOUND")
            all_ok = False
    
    return all_ok


def check_mcp_server():
    """Check if MCP server can be imported"""
    print("\n" + "=" * 70)
    print("CHECKING MCP SERVER")
    print("=" * 70)
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
        from mcp import server
        print("✅ MCP server module loads successfully")
        return True
    except Exception as e:
        print(f"⚠️  MCP server loading issue: {e}")
        return False


def print_summary(results):
    """Print final summary"""
    print("\n" + "=" * 70)
    print("HEALTH CHECK SUMMARY")
    print("=" * 70 + "\n")
    
    checks = [
        ("Python Version", results["python"]),
        ("Dependencies", results["dependencies"]),
        ("Environment Variables", results["env_vars"]),
        (".env File", results["env_file"]),
        ("Config Module", results["config"]),
        ("Core Components", results["components"]),
        ("Standalone Scripts", results["scripts"]),
        ("MCP Server", results["mcp"]),
    ]
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed\n")
    
    if passed == total:
        print("🎉 Email Bridge is ready to use!")
        print("\nNext steps:")
        print("  1. Run once: python standalone/bot.py")
        print("  2. Run daily: python standalone/scheduler.py")
        print("  3. Or use as MCP: python mcp/server.py")
        return True
    else:
        print("⚠️  Some checks failed. See above for details.")
        return False


def main():
    """Run all health checks"""
    print("\n" + "🏥 EMAIL BRIDGE HEALTH CHECK" + " " * 40)
    
    results = {
        "python": check_python_version(),
        "dependencies": check_dependencies(),
        "env_file": check_env_file(),
        "env_vars": check_environment_variables(),
        "config": check_config_module(),
        "components": check_components_import(),
        "scripts": check_standalone_scripts(),
        "mcp": check_mcp_server(),
    }
    
    success = print_summary(results)
    
    if not success and results["env_vars"] is False:
        print("\n" + "=" * 70)
        print("SETUP GUIDE")
        print("=" * 70)
        
        sys.path.insert(0, ".")
        try:
            from core.config import ConfigValidator
            ConfigValidator.print_setup_guide()
        except Exception:
            pass
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
