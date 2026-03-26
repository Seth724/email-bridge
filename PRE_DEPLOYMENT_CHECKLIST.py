#!/usr/bin/env python3
"""
Email Bridge - Pre-Deployment Verification Checklist

This guide ensures every component is tested before production deployment.

Run these checks in order, one by one.
"""

# ============================================================================
# PART A: ENVIRONMENT VALIDATION
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║         EMAIL BRIDGE - PRE-DEPLOYMENT VERIFICATION CHECKLIST              ║
║                                                                            ║
║ This checklist ensures Email Bridge is ready for production deployment.    ║
║ Complete each check in order.                                             ║
╚════════════════════════════════════════════════════════════════════════════╝

PART A: ENVIRONMENT & CONFIGURATION
═════════════════════════════════════════════════════════════════════════════

[ ] 1. Verify .env file exists
    └─ Command: ls -la .env
    └─ Expected: File should exist with values

[ ] 2. Check all required variables are set
    └─ Command: python tests/health_check.py
    └─ Expected: ✅ All environment variables

[ ] 3. Verify configuration loads
    └─ Command: python -c "from core.config import ConfigValidator; ConfigValidator.validate()"
    └─ Expected: No errors, configuration validated

[ ] 4. Test Gmail connection specifically
    └─ Command: python -c "
      from core.gmail import GmailFetcher
      import os
      gmail = GmailFetcher(os.getenv('GMAIL_ADDRESS'), os.getenv('GMAIL_APP_PASSWORD'))
      if gmail.connect():
          count = gmail.get_email_count()
          print(f'✅ Connected to Gmail. Unread: {count}')
          gmail.disconnect()
      else:
          print('❌ Failed to connect')
      "
    └─ Expected: ✅ Connected message

[ ] 5. Test Telegram bot token
    └─ Command: python -c "
      from core.telegram import TelegramSender
      import os
      telegram = TelegramSender(os.getenv('TELEGRAM_BOT_TOKEN'), os.getenv('TELEGRAM_CHAT_ID'))
      bot = telegram.get_me()
      if bot:
          print(f'✅ Telegram bot verified: @{bot.get(\"username\", \"bot\")}')
      else:
          print('❌ Invalid Telegram token')
      "
    └─ Expected: ✅ Telegram bot verified

═════════════════════════════════════════════════════════════════════════════

PART B: COMPONENT TESTING
═════════════════════════════════════════════════════════════════════════════

[ ] 6. Verify all core modules load
    └─ Command: python tests/verify_system.py
    └─ Look for: "10. MCP SERVER SETUP" section should pass

[ ] 7. Test email classifier
    └─ Command: python -c "
      from core.classifier import EmailClassifier
      import os
      classifier = EmailClassifier(api_key=os.getenv('GROQ_API_KEY'))
      email = {
          'subject': 'URGENT: Server down',
          'sender': 'admin@example.com',
          'body': 'Production server is offline'
      }
      result = classifier.classify_email(email)
      print(f'✅ Classified as: {result[\"category\"]}, Confidence: {result[\"confidence\"]}')
      "
    └─ Expected: ✅ Classified as URGENT or similar

[ ] 8. Test rules engine
    └─ Command: python -c "
      from core.rules_engine import RulesEngine
      rules = RulesEngine()
      if rules.is_loaded():
          print('✅ Rules engine loaded')
      else:
          print('⚠️  Rules file not found')
      "
    └─ Expected: ✅ Rules engine loaded

[ ] 9. Test time urgency logic
    └─ Command: python -c "
      from core.time_urgency import TimeUrgencyManager
      from datetime import datetime
      manager = TimeUrgencyManager()
      now = datetime.now()
      print(f'Current time: {now.strftime(\"%H:%M\")}')
      print(f'In quiet hours (22:00-07:00): {manager.is_quiet_hours()}')
      print(f'Is weekend: {manager.is_weekend()}')
      print('✅ Time logic working')
      "
    └─ Expected: ✅ Time logic working

═════════════════════════════════════════════════════════════════════════════

PART C: WORKFLOW TESTING
═════════════════════════════════════════════════════════════════════════════

[ ] 10. Test complete email triage workflow
    └─ Command: python -c "
      from core.classifier import EmailClassifier
      from workflows.triage_graph import EmailTriageWorkflow
      from datetime import datetime
      import os
      
      classifier = EmailClassifier(api_key=os.getenv('GROQ_API_KEY'))
      workflow = EmailTriageWorkflow(classifier)
      
      test_emails = [
          {
              'id': '1',
              'subject': 'URGENT: Issue',
              'sender': 'boss@company.com',
              'body': 'Critical problem',
              'date': datetime.now().isoformat(),
          },
          {
              'id': '2',
              'subject': 'Meeting reminder',
              'sender': 'team@company.com',
              'body': 'Team standup tomorrow',
              'date': datetime.now().isoformat(),
          },
      ]
      
      result = workflow.process_emails(test_emails)
      print(f'✅ Workflow executed')
      print(f'   Classified: {len(result[\"classified_emails\"])}')
      print(f'   Urgent: {len(result[\"urgent_emails\"])}')
      print(f'   Important: {len(result[\"important_emails\"])}')
      "
    └─ Expected: ✅ Workflow executed with counts

═════════════════════════════════════════════════════════════════════════════

PART D: STANDALONE BOT TEST
═════════════════════════════════════════════════════════════════════════════

[ ] 11. Test standalone bot (one-time execution)
    └─ Command: python standalone/bot.py
    └─ Expected output:
      ├─ Connected to Gmail ✅
      ├─ Found X unread emails ✅
      ├─ Classified X emails ✅
      ├─ Marked emails as read ✅
      └─ Email check completed ✅
    
    └─ What's happening:
      ├─ Connects to Gmail IMAP
      ├─ Fetches unread emails from last 24h
      ├─ Classifies using AI + rules engine
      ├─ Checks time-based rules (quiet hours)
      ├─ Sends Telegram message (if appropriate)
      └─ Marks emails as read to prevent duplicates

[ ] 12. Check Telegram notification received
    └─ If running at 7 AM - 10 PM:
      └─ Should receive message in Telegram ✅
    └─ If running at 10 PM - 7 AM:
      └─ Quiet hours mode: No message (intentional) ✅
    
    └─ Troubleshooting:
      ├─ No message? Check TELEGRAM_CHAT_ID
      ├─ Wrong app? Verify bot token is correct
      ├─ Error in Telegram? Check logs for "Telegram API error"

═════════════════════════════════════════════════════════════════════════════

PART E: SCHEDULER TEST
═════════════════════════════════════════════════════════════════════════════

[ ] 13. Test scheduler initialization
    └─ Command: python -c "
      import os
      from apscheduler.schedulers.blocking import BlockingScheduler
      print('✅ APScheduler loaded')
      print(f'Schedule time: {os.getenv(\"SCHEDULE_HOUR\", \"7\")}:{os.getenv(\"SCHEDULE_MINUTE\", \"0\")}')
      print(f'Timezone: {os.getenv(\"TIMEZONE\", \"UTC\")}')
      "
    └─ Expected: ✅ APScheduler loaded with your schedule

[ ] 14. Test scheduler dry-run (don't start continuous)
    └─ Command: python -c "
      import os
      from apscheduler.schedulers.blocking import BlockingScheduler
      
      hour = int(os.getenv('SCHEDULE_HOUR', '7'))
      minute = int(os.getenv('SCHEDULE_MINUTE', '0'))
      tz = os.getenv('TIMEZONE', 'UTC')
      
      scheduler = BlockingScheduler(timezone=tz)
      scheduler.add_job(
          lambda: print('✅ Job would run here'),
          trigger='cron',
          hour=hour,
          minute=minute,
          replace_existing=True,
      )
      
      print(f'⏰ Scheduler would run daily at {hour}:{minute:02d} {tz}')
      print('✅ Scheduler configuration is valid')
      # Don't actually start - would block terminal
      "
    └─ Expected: ✅ Scheduler configuration is valid

═════════════════════════════════════════════════════════════════════════════

PART F: MCP SERVER TEST
═════════════════════════════════════════════════════════════════════════════

[ ] 15. Verify MCP server loads
    └─ Command: python -c "
      from mcp import server
      print('✅ MCP server module loads')
      print('Ready for Claude Desktop integration')
      "
    └─ Expected: ✅ MCP server module loads

[ ] 16. Check MCP tools are available
    └─ Tools available:
      ├─ check_emails() - Fetch and classify emails
      ├─ get_urgent_summary() - Urgent emails only
      ├─ send_telegram_message() - Send custom message
      ├─ test_connection() - Verify all APIs
      └─ classify_email_sample() - Test AI classifier

═════════════════════════════════════════════════════════════════════════════

PART G: FULL INTEGRATION TEST
═════════════════════════════════════════════════════════════════════════════

[ ] 17. Run complete system verification
    └─ Command: python tests/verify_system.py
    └─ Expected: All 10 checks pass ✅
    
    └─ Checks performed:
      ├─ Python version (3.10+)
      ├─ All dependencies installed
      ├─ Environment variables
      ├─ Gmail connection
      ├─ Email classifier
      ├─ Telegram connection
      ├─ Time-based logic
      ├─ Email triage workflow
      ├─ Rules engine
      └─ MCP server

═════════════════════════════════════════════════════════════════════════════

PART H: FINAL DEPLOYMENT CHECKLIST
═════════════════════════════════════════════════════════════════════════════

Before going live, verify:

[ ] Security
    ├─ [ ] .env file is in .gitignore
    ├─ [ ] No API keys in any Python files
    ├─ [ ] App-specific password (not regular Gmail password)
    └─ [ ] All credentials in environment variables only

[ ] Testing
    ├─ [ ] All 17 checks above passed
    ├─ [ ] Logs look normal (check for errors)
    ├─ [ ] Received test Telegram message
    └─ [ ] Bot handles errors gracefully

[ ] Scheduling
    ├─ [ ] Decided on deployment mode:
    │   ├─ [ ] Local scheduler (python standalone/scheduler.py &)
    │   ├─ [ ] Cloud deployment (Railway/Render)
    │   ├─ [ ] GitHub Actions (free)
    │   └─ [ ] Claude Desktop (MCP)
    └─ [ ] Set up permanent running (cron/systemd/cloud)

[ ] Monitoring
    ├─ [ ] Check Telegram messages arriving at 7 AM
    ├─ [ ] Review logs periodically
    ├─ [ ] Monitor API costs (should be < $1/month)
    └─ [ ] Adjust quiet hours if needed

═════════════════════════════════════════════════════════════════════════════

DEPLOYMENT INSTRUCTIONS BY MODE
═════════════════════════════════════════════════════════════════════════════

MODE 1: LOCAL SCHEDULER (RECOMMENDED FOR PERSONAL USE)
───────────────────────────────────────────────────────

Steps:
  1. Run: python standalone/scheduler.py &
  2. Runs daily at 7 AM (configurable)
  3. Runs weekly summary Sunday 8 PM
  4. Respects quiet hours (22:00-07:00)
  5. Marks emails as read to prevent duplicates

Pros:
  ✅ Free
  ✅ Simple setup
  ✅ Full control
  ✅ No cloud costs

Cons:
  ❌ Requires always-on computer
  ❌ Lost if system restarts without auto-start

Auto-start setup (Windows):
  1. Create batch file: run_emailbridge.bat
  2. Content: @echo off
             cd D:\MetaruneLabs\mcp-server\email-bridge
             python standalone/scheduler.py
  3. Add to Task Scheduler (run at startup)

Auto-start setup (Linux/Mac):
  1. Install as systemd service
  2. Add to crontab: 0 7 * * * /usr/bin/python3 ~/email-bridge/standalone/scheduler.py


MODE 2: CLOUD DEPLOYMENT (RECOMMENDED FOR 24/7)
────────────────────────────────────────────────

Deploy to Railway (free tier, then $5/month):
  1. Go to https://railway.app
  2. Create new project
  3. Connect your GitHub repo
  4. Add environment variables (secrets)
  5. Deployment happens automatically

Deploy to Render:
  1. Go to https://render.com
  2. New "Background Worker"
  3. Set command: python standalone/scheduler.py
  4. Add environment variables
  
Cost: ~$5-10/month (includes always-on monitoring)


MODE 3: GITHUB ACTIONS (FREE, RECOMMENDED FOR SIMPLICITY)
──────────────────────────────────────────────────────────

Runs daily at 7 AM (free for public repos):
  1. Already set up in .github/workflows/
  2. Push to GitHub
  3. Add secrets in GitHub Settings
  4. Runs automatically every day at 7 AM UTC

Cost: Free (up to 2000 minutes/month free)


MODE 4: CLAUDE DESKTOP MCP SERVER
──────────────────────────────────

Integrate with Claude AI assistant:
  1. Edit ~/.config/claude/claude_desktop_config.json
  2. Add Email Bridge server config
  3. Ask Claude: "Check my important emails"
  4. Claude can access all tools

Cost: Free (uses your existing Claude subscription)


═════════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING COMMON ISSUES
═════════════════════════════════════════════════════════════════════════════

Issue: "No Telegram message received"
─────────────────────────────────────
Possible causes:
  1. Running during quiet hours (22:00-07:00)
     → Solution: Run during business hours for testing
  
  2. No urgent/important emails found
     → Solution: Check logs for "Found 0 urgent"
     → Expected if all emails are newsletters
  
  3. Wrong TELEGRAM_CHAT_ID
     → Solution: Get from getUpdates API
     → Visit: https://api.telegram.org/bot<TOKEN>/getUpdates
  
  4. Bot token is invalid
     → Solution: Recreate bot with @BotFather
     → Copy token again carefully


Issue: "Gmail connection failed"
────────────────────────────────
Possible causes:
  1. Wrong app password (should be 16 chars)
     → Solution: Get new one from Google Account
     → Settings → Security → App passwords
  
  2. Not using 2FA
     → Solution: Enable 2FA on Google Account
     → Required for app passwords
  
  3. Email address is wrong
     → Solution: Double-check GMAIL_ADDRESS
     → Must be full email: user@gmail.com


Issue: "Groq API error / Rate limited"
──────────────────────────────────────
Possible causes:
  1. Invalid API key
     → Solution: Get new one from https://console.groq.com/
  
  2. Rate limited (free tier: 30 calls/minute)
     → Solution: Normal - wait a minute, retries automatically
  
  3. Model not available
     → Solution: Try different model in GROQ_MODEL env var


Issue: "Scheduler time is wrong"
────────────────────────────────
Solution:
  1. Check TIMEZONE setting in .env
     → Currently: UTC
     → Change to: America/New_York, Europe/London, etc.
  
  2. Check SCHEDULE_HOUR
     → Currently: 7 (7 AM)
     → Change as needed
  
  3. Verify system time is correct
     → Run: date (Linux/Mac) or time (Windows)


═════════════════════════════════════════════════════════════════════════════

NEXT STEPS AFTER DEPLOYMENT
═════════════════════════════════════════════════════════════════════════════

Day 1:
  [ ] Set up scheduler (choose mode above)
  [ ] Verify 7 AM message arrives in Telegram
  [ ] Check logs for any errors

Week 1:
  [ ] Monitor messages arriving
  [ ] Adjust quiet hours if needed
  [ ] Customize rules.ini with your senders
  [ ] Check email filtering accuracy

Month 1:
  [ ] Monitor API costs (should be < $1)
  [ ] Review classification accuracy
  [ ] Adjust rules as patterns emerge
  [ ] Consider setup for other email accounts (if needed)

═════════════════════════════════════════════════════════════════════════════

SUPPORT & DOCUMENTATION
═════════════════════════════════════════════════════════════════════════════

Key files to reference:
  • README.md - Overview and quick start
  • QUICKSTART.md - 5-minute setup
  • WHAT_EVERYTHING_DOES.md - Complete explanation
  • PRODUCTION_READINESS.md - Deployment guide
  • ARCHITECTURE.md - Technical details
  • DEPLOYMENT.md - Cloud deployment

Code files:
  • core/gmail.py - Gmail IMAP fetcher
  • core/classifier.py - Email classifier
  • core/telegram.py - Telegram sender
  • core/rules_engine.py - Custom rules
  • core/time_urgency.py - Quiet hours logic
  • workflows/triage_graph.py - Main workflow
  • standalone/bot.py - Manual checker
  • standalone/scheduler.py - Daily automation
  • mcp/server.py - Claude Desktop integration

═════════════════════════════════════════════════════════════════════════════

FINAL SIGN-OFF
═════════════════════════════════════════════════════════════════════════════

If you've completed all checks above and they all passed:

    ✅ EMAIL BRIDGE IS READY FOR PRODUCTION DEPLOYMENT

Next: Choose a deployment mode and set it up for continuous operation!

═════════════════════════════════════════════════════════════════════════════
""")

# Run this to print the checklist
if __name__ == "__main__":
    print("\n📋 Checklist complete. See above for all verification steps.")
