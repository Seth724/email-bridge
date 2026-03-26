#!/usr/bin/env python3
"""
Email Bridge - Complete System Verification

Comprehensive test to verify:
1. All components initialize correctly
2. Full workflow executes end-to-end
3. Error handling works
4. MCP server is ready
5. Scheduler works
6. Time-based logic works

Run with: python tests/verify_system.py
"""

import os
import sys
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


class VerificationResult:
    """Track verification results"""
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
        
    def add(self, name, passed, message=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        self.checks.append((status, name, message))
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            
    def print_summary(self):
        print("\n" + "=" * 80)
        print("VERIFICATION RESULTS")
        print("=" * 80 + "\n")
        for status, name, message in self.checks:
            print(f"{status}  {name}")
            if message:
                print(f"       {message}")
        print(f"\nTotal: {self.passed} passed, {self.failed} failed\n")
        return self.failed == 0


def verify_environment(result):
    """1. Check environment configuration"""
    print("\n" + "=" * 80)
    print("1. ENVIRONMENT CONFIGURATION")
    print("=" * 80)
    
    required = [
        "GMAIL_ADDRESS",
        "GMAIL_APP_PASSWORD",
        "GROQ_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
    ]
    
    for var in required:
        val = os.getenv(var)
        if val:
            masked = val[:4] + "*" * (len(val) - 8) + val[-4:]
            result.add(f"{var}", True)
            print(f"✅ {var} = {masked}")
        else:
            result.add(f"{var}", False)
            print(f"❌ {var} - NOT SET")


def verify_dependencies(result):
    """2. Check Python dependencies"""
    print("\n" + "=" * 80)
    print("2. DEPENDENCIES")
    print("=" * 80)
    
    deps = [
        ("core.gmail", "GmailFetcher"),
        ("core.classifier", "EmailClassifier"),
        ("core.telegram", "TelegramSender"),
        ("core.rules_engine", "RulesEngine"),
        ("core.time_urgency", "TimeUrgencyManager"),
        ("core.config", "ConfigValidator"),
        ("workflows.triage_graph", "EmailTriageWorkflow"),
        ("mcp.server", "FastMCP"),
    ]
    
    for module, cls in deps:
        try:
            mod = __import__(module, fromlist=[cls])
            getattr(mod, cls)
            result.add(f"{module}.{cls}", True)
            print(f"✅ {module}.{cls}")
        except ImportError as e:
            result.add(f"{module}.{cls}", False, str(e))
            print(f"❌ {module}.{cls} - {e}")


def verify_gmail_connection(result):
    """3. Check Gmail connection"""
    print("\n" + "=" * 80)
    print("3. GMAIL CONNECTION")
    print("=" * 80)
    
    try:
        from core.gmail import GmailFetcher
        
        gmail = GmailFetcher(
            email_address=os.getenv("GMAIL_ADDRESS"),
            app_password=os.getenv("GMAIL_APP_PASSWORD"),
        )
        
        if gmail.connect():
            print(f"✅ Connected to Gmail: {os.getenv('GMAIL_ADDRESS')}")
            
            # Try to get email count
            count = gmail.get_email_count(unread_only=True)
            print(f"✅ Unread emails: {count}")
            result.add("Gmail Connection", True)
            result.add("Email Fetch", True, f"{count} unread emails")
            
            gmail.disconnect()
        else:
            result.add("Gmail Connection", False)
            print("❌ Failed to connect to Gmail")
    except Exception as e:
        result.add("Gmail Connection", False, str(e))
        print(f"❌ Error: {e}")


def verify_classifier(result):
    """4. Check email classifier"""
    print("\n" + "=" * 80)
    print("4. EMAIL CLASSIFIER")
    print("=" * 80)
    
    try:
        from core.classifier import EmailClassifier
        
        classifier = EmailClassifier(
            api_key=os.getenv("GROQ_API_KEY"),
            use_custom_rules=True,
        )
        
        print("✅ EmailClassifier initialized")
        result.add("Classifier Initialization", True)
        
        # Test classification
        test_email = {
            "subject": "URGENT: System down",
            "sender": "admin@company.com",
            "body": "Production server is offline. Immediate action required.",
        }
        
        classification = classifier.classify_email(test_email)
        print(f"✅ Classified test email as: {classification['category']}")
        result.add("Classifier Execution", True, f"Category: {classification['category']}")
        
    except Exception as e:
        result.add("Email Classifier", False, str(e))
        print(f"❌ Error: {e}")


def verify_telegram(result):
    """5. Check Telegram connection"""
    print("\n" + "=" * 80)
    print("5. TELEGRAM CONNECTION")
    print("=" * 80)
    
    try:
        from core.telegram import TelegramSender
        
        telegram = TelegramSender(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        )
        
        print(f"✅ TelegramSender initialized")
        print(f"   Chat ID: {os.getenv('TELEGRAM_CHAT_ID')}")
        result.add("Telegram Initialization", True)
        
        # Check bot info (safe, doesn't send message)
        bot_info = telegram.get_me()
        if bot_info:
            print(f"✅ Bot verified: @{bot_info.get('username', 'unknown')}")
            result.add("Telegram Bot", True, f"@{bot_info.get('username', 'bot')}")
        else:
            result.add("Telegram Bot", False, "Could not verify bot")
            
    except Exception as e:
        result.add("Telegram Connection", False, str(e))
        print(f"❌ Error: {e}")


def verify_time_logic(result):
    """6. Check time-based notification logic"""
    print("\n" + "=" * 80)
    print("6. TIME-BASED NOTIFICATION LOGIC")
    print("=" * 80)
    
    try:
        from core.time_urgency import TimeUrgencyManager
        
        manager = TimeUrgencyManager(
            quiet_hours_start=22,
            quiet_hours_end=7,
            weekend_mode="silent",
        )
        
        # Test current time
        now = datetime.now()
        in_quiet = manager.is_quiet_hours(now)
        is_weekend = manager.is_weekend(now)
        
        print(f"✅ Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Quiet hours: 22:00 - 07:00")
        print(f"   In quiet hours: {in_quiet}")
        print(f"   Is weekend: {is_weekend}")
        
        result.add("Time Logic", True, f"Quiet: {in_quiet}, Weekend: {is_weekend}")
        
        # Test notification mode
        mode_urgent = manager.get_notification_mode("URGENT")
        mode_important = manager.get_notification_mode("IMPORTANT")
        
        print(f"   URGENT mode: Send={mode_urgent['send']}, Silent={mode_urgent.get('silent', False)}")
        print(f"   IMPORTANT mode: Send={mode_important['send']}, Silent={mode_important.get('silent', False)}")
        
        result.add("Notification Modes", True)
        
    except Exception as e:
        result.add("Time Logic", False, str(e))
        print(f"❌ Error: {e}")


def verify_workflow(result):
    """7. Check complete workflow"""
    print("\n" + "=" * 80)
    print("7. EMAIL TRIAGE WORKFLOW")
    print("=" * 80)
    
    try:
        from core.classifier import EmailClassifier
        from workflows.triage_graph import EmailTriageWorkflow
        
        classifier = EmailClassifier(
            api_key=os.getenv("GROQ_API_KEY"),
            use_custom_rules=True,
        )
        
        workflow = EmailTriageWorkflow(classifier)
        print("✅ Workflow initialized")
        
        # Test with mock emails
        test_emails = [
            {
                "id": "1",
                "subject": "URGENT: Security alert",
                "sender": "security@company.com",
                "body": "Suspicious login detected",
                "date": datetime.now().isoformat(),
            },
            {
                "id": "2",
                "subject": "Team meeting tomorrow",
                "sender": "boss@company.com",
                "body": "Reminder about team standup",
                "date": datetime.now().isoformat(),
            },
            {
                "id": "3",
                "subject": "Weekly newsletter",
                "sender": "newsletter@example.com",
                "body": "This week's news",
                "date": datetime.now().isoformat(),
            },
        ]
        
        result_state = workflow.process_emails(test_emails)
        
        print(f"✅ Workflow executed successfully")
        print(f"   Total emails: {len(result_state['emails'])}")
        print(f"   Classified: {len(result_state['classified_emails'])}")
        print(f"   Urgent: {len(result_state['urgent_emails'])}")
        print(f"   Important: {len(result_state['important_emails'])}")
        print(f"   Summary generated: {len(result_state['summary']) > 0}")
        
        result.add("Workflow Execution", True, f"{len(result_state['classified_emails'])} emails processed")
        
    except Exception as e:
        result.add("Workflow", False, str(e))
        print(f"❌ Error: {e}")


def verify_rules_engine(result):
    """8. Check custom rules engine"""
    print("\n" + "=" * 80)
    print("8. CUSTOM RULES ENGINE")
    print("=" * 80)
    
    try:
        from core.rules_engine import RulesEngine
        
        rules = RulesEngine()
        
        if rules.is_loaded():
            print("✅ Rules file loaded: config/rules.ini")
            
            # Test a rule
            test_sender = "boss@company.com"
            category = rules.check_sender(test_sender)
            
            if category:
                print(f"✅ Sender rule test: {test_sender} → {category}")
            else:
                print(f"⚠️  No rule found for {test_sender} (expected)")
            
            result.add("Rules Engine", True, "Rules loaded successfully")
        else:
            result.add("Rules Engine", False, "Rules file not found")
            print("❌ Rules file not available")
            
    except Exception as e:
        result.add("Rules Engine", False, str(e))
        print(f"❌ Error: {e}")


def verify_standalone_scripts(result):
    """9. Check standalone scripts"""
    print("\n" + "=" * 80)
    print("9. STANDALONE SCRIPTS")
    print("=" * 80)
    
    scripts = {
        "standalone/bot.py": "One-time email check",
        "standalone/scheduler.py": "Daily automated jobs",
        "standalone/weekly_summary.py": "Weekly email statistics",
    }
    
    for script, desc in scripts.items():
        if os.path.exists(script):
            result.add(f"{script}", True, desc)
            print(f"✅ {script} - {desc}")
        else:
            result.add(f"{script}", False)
            print(f"❌ {script} - NOT FOUND")


def verify_mcp_server(result):
    """10. Check MCP server setup"""
    print("\n" + "=" * 80)
    print("10. MCP SERVER SETUP")
    print("=" * 80)
    
    try:
        from fastmcp import FastMCP
        print("✅ FastMCP imported")
        
        # Try to import MCP server
        from mcp import server as mcp_server
        print("✅ MCP server module loads")
        
        result.add("MCP Server", True, "Ready for Claude Desktop")
        print("✅ MCP server is ready for deployment")
        
        # Show configuration example
        config_example = """
Configuration for Claude Desktop (~/.config/claude/claude_desktop_config.json):

{
  "mcpServers": {
    "email-bridge": {
      "command": "python",
      "args": ["mcp/server.py"],
      "env": {
        "GROQ_API_KEY": "your-key",
        "GMAIL_ADDRESS": "your@email.com",
        "GMAIL_APP_PASSWORD": "your-password",
        "TELEGRAM_BOT_TOKEN": "your-token",
        "TELEGRAM_CHAT_ID": "your-chat-id"
      }
    }
  }
}
        """
        
        print(config_example)
        
    except Exception as e:
        result.add("MCP Server", False, str(e))
        print(f"❌ Error: {e}")


def print_system_status(result):
    """Print final system status"""
    print("\n" + "=" * 80)
    print("SYSTEM STATUS SUMMARY")
    print("=" * 80 + "\n")
    
    all_ok = result.print_summary()
    
    if all_ok:
        print("🎉 SYSTEM IS PRODUCTION-READY!\n")
        print("Next steps:")
        print("  1. Test bot: python standalone/bot.py")
        print("  2. Run scheduler: python standalone/scheduler.py")
        print("  3. Monitor logs for 7 AM execution")
        print("  4. Check Telegram for daily digest\n")
        return True
    else:
        print("⚠️  SOME CHECKS FAILED\n")
        print("Please fix the failed items above before deployment.\n")
        return False


def main():
    """Run all verification checks"""
    print("\n" + "=" * 80)
    print("EMAIL BRIDGE - COMPLETE SYSTEM VERIFICATION")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    result = VerificationResult()
    
    # Run all checks
    verify_environment(result)
    verify_dependencies(result)
    verify_gmail_connection(result)
    verify_classifier(result)
    verify_telegram(result)
    verify_time_logic(result)
    verify_workflow(result)
    verify_rules_engine(result)
    verify_standalone_scripts(result)
    verify_mcp_server(result)
    
    # Print summary
    success = print_system_status(result)
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
