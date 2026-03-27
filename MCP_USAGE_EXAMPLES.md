# Email Bridge MCP - Claude Conversation Examples

**Real-world examples of how to use Email Bridge with Claude Desktop.**

---

## Example 1: Check Urgent Emails (Most Common)

### You Ask:
```
What urgent emails do I have?
```

### Claude Does:
```
I'll check your urgent emails for you.
[Calling tool: get_urgent_summary()]
```

### You Get:
```
🚨 URGENT EMAILS (2):

1. **Security Alert** - Google <no-reply@accounts.google.com>
   Summary: App password created for your account
   When: Today at 3:47 PM
   Action: ⚡ Check account activity and verify you authorized this

2. **Password Reset** - Microsoft <account-security-noreply@accountprotection.microsoft.com>
   Summary: Security info was added to your account
   When: Today at 1:33 PM
   Action: ⚡ Review recent activity if you didn't do this
```

---

## Example 2: Full Email Summary

### You Ask:
```
Give me a summary of all my emails today. What do I need to handle?
```

### Claude Does:
```
Let me fetch and analyze your emails.
[Calling tool: check_emails(limit=20, days_back=1)]
```

### You Get:
```
📊 **Your Email Summary**

🚨 **URGENT (3)** - ACTION REQUIRED:
├─ Security Alert from Google
│  └─ Someone accessed your account - verify activity
├─ Microsoft Account Alert
│  └─ Security setting changed - confirm if you did this
└─ Bank Transaction Alert
   └─ $500 charge from AWS - approve or dispute

📌 **IMPORTANT (5)** - THIS WEEK:
├─ Meeting invite: Project Sync (Wed 2 PM)
├─ Invoice from AWS
├─ Slack notification
├─ GitHub issue assigned to you
└─ Weekly Team Newsletter

📄 **NORMAL (12)**
├─ Promotional emails
├─ Notifications
└─ Confirmations

💡 **AI Analysis:**
- 3 urgent items require immediate attention
- 2 of the urgent items are security-related
- Recommend: Reset passwords and enable 2FA on Google/Microsoft
- Top priority: Verify the AWS charge (high amount)

**Quick Actions:**
1. Confirm AWS charge or contact support
2. Verify security alerts aren't compromised password
3. Accept meeting invite
```

---

## Example 3: Send Alert to Telegram

### You Ask:
```
Send this message to Telegram: "Important meeting moved to 3 PM today"
```

### Claude Does:
```
I'll send that to your Telegram right away.
[Calling tool: send_telegram_message(message: "Important meeting moved to 3 PM today", urgent: false)]
```

### You Get:
```
✅ Message sent successfully!
You'll receive it on your phone instantly.
```

### What Happens on Your Phone:
Your Telegram app shows:
```
My Email Assistant [3:45 PM]
Important meeting moved to 3 PM today
```

---

## Example 4: Send Urgent Alert to Telegram

### You Ask:
```
Send urgent: "Your bank detected suspicious activity. Review immediately."
```

### Claude Does:
```
I'll send this as an urgent alert with notification.
[Calling tool: send_telegram_message(message: "...", urgent: true)]
```

### You Get:
```
✅ Urgent alert sent!
Your phone will receive a loud notification.
```

### What Happens on Your Phone:
Telegram **buzzes with notification sound** and shows:
```
🚨 My Email Assistant [ALERT]
Your bank detected suspicious activity. Review immediately.
```

---

## Example 5: Morning Briefing Routine

### You Ask:
```
Give me my morning email briefing. Focus on what needs action today.
```

### Claude Does:
```
Let me prepare your morning briefing.
[Calling tool: check_emails()]
[Analyzing results...]
```

### You Get:
```
📧 **Morning Email Briefing** - March 27, 2026

⚡ **ACTIONS NEEDED TODAY (3):**
1. [SECURITY] Verify Google account login from new device
   └─ Action: Click link in Google email, review recent activity
   
2. [FINANCE] Approve $500 AWS charge or contact support
   └─ Action: Check AWS billing details, confirm legitimate
   
3. [MEETING] Accept calendar invite for Project Sync
   └─ Action: Confirm attendance by EOD

📋 **IMPORTANT BUT NOT URGENT (2):**
- Invoice to process (due next week)
- Team newsletter with updates

✅ **ALL CLEAR:**
- 12 normal emails (promotions, notifications, etc.)

⏰ **TODAY'S SCHEDULE:**
- 2:00 PM - Project Sync Meeting
- [No other calendar conflicts]

🎯 **YOUR PRIORITIES:**
1. First: Security alerts (check account activity)
2. Second: AWS charge verification
3. Third: Accept meeting

💰 **COST**: 5 classified emails = ~$0.005 in Groq API fees
```

---

## Example 6: Analyze Suspicious Email

### You Ask:
```
I got an email from "Apple Support" saying my account is locked. Is this a scam?
Can you look at it and tell me if it's legit?
```

### Claude Does:
```
I'll check your emails and analyze that one for you.
[Calling tool: check_emails()]
[Analyzing for phishing patterns...]
```

### You Get:
```
🚨 **PHISHING ALERT** - This looks like a scam!

Email Details:
- From: apple_support_verify@appleupdate.com ❌ WRONG SENDER
- Subject: "Your Apple ID Has Been Compromised"
- Links: appleupdate-security.com ❌ NOT OFFICIAL

Red Flags:
✗ Sender email doesn't match official Apple domain (@apple.com)
✗ Apple rarely locks accounts without warning first
✗ URL is suspicious (not verify.apple.com)
✗ Requests immediate password entry (classic phishing)
✗ Urgency + fear tactic (locked account)

Legitimate Apple emails:
✓ Come from @apple.com
✓ Never ask you to click links for passwords
✓ Have proper formatting and Apple branding

**Recommendation:** 
🚫 DELETE this email
🔒 Check your actual Apple account at apple.com directly
🔐 Change your Apple password if you clicked any links
📧 Report as phishing to Apple

Very likely: **Phishing attempt**
Confidence: 95%
```

---

## Example 7: Week in Review

### You Ask:
```
What happened in my emails this week? Any patterns I should know about?
```

### Claude Does:
```
Let me gather your emails from the past week.
[Calling tool: check_emails(days_back=7, limit=50)]
[Analyzing patterns...]
```

### You Get:
```
📊 **WEEK IN REVIEW** (March 21-27, 2026)

📈 **Email Volume:**
- Total: 47 emails
- Urgent: 5
- Important: 12
- Normal: 30

🔍 **Patterns I Notice:**

1. **Security Alerts (3 emails)**
   └─ Google, Microsoft, AWS all sent alerts
   └─ Likely: New app passwords / 2FA changes you made
   └─ Action: Verify you authorized all of these

2. **Project Communication (5 emails)**
   └─ Team meeting invites, updates, status reports
   └─ Status: All attended/confirmed

3. **Financial (4 emails)**
   └─ AWS billing, invoice notifications
   └─ Amount: ~$1,200 this week
   └─ Action: Review AWS cost increase

4. **Marketing/Promotional (20+ emails)**
   └─ Newsletters, sales, notifications
   └─ Recommendation: Unsubscribe from unnecessary ones

⚠️ **Anomalies:**
- 3x more security alerts than normal
- Can suggest: Review 2FA settings, ensure no account breach
- AWS costs up 40% from last week

💡 **This Week's Insights:**
1. You're receiving too many promotional emails (80% of volume)
2. Security activity is higher than normal (good sign of vigilance)
3. Finance alerts suggest you're actively managing cloud resources
4. Team communication is healthy (good collaboration)

🎯 **Recommendations:**
1. Unsubscribe from 5+ promotional subscriptions
2. Create email rules to auto-archive promotions
3. Verify AWS cost increase (might optimize)
4. Consider enabling Do Not Disturb during meetings
```

---

## Example 8: Automated Email to Telegram Bridge

### You Ask:
```
Whenever I get an urgent email, automatically send a summary to my Telegram.
Can you set that up?
```

### Claude Does:
```
I can help you create a monitoring loop. Let me set up automatic checking.

[Creating a monitoring task...]
I'll check your emails every 5 minutes and forward urgent ones to Telegram.
```

### What Happens:
```
🔄 **Email Monitor Active**

Every 5 minutes:
1. Check for new unread emails
2. Classify them (urgent/important/normal)
3. If URGENT found:
   └─ Send alert to Telegram with summary
4. Mark email as read

You stay updated on your phone without leaving Claude!
```

### Example Telegram Flow:
```
[2:15 PM] 🚨 NEW URGENT EMAIL
From: Security Center <security@bank.com>
Subject: Suspicious Login Detected
Action: Verify location or password

[2:22 PM] Bank response received
Reply to this message to forward to email...
```

---

## Example 9: Test Connections

### You Ask:
```
Is everything connected? Can you test Gmail and Telegram for me?
```

### Claude Does:
```
I'll run a connection test.
[Calling tool: test_connection()]
```

### You Get:
```
✅ **Connection Status: All Systems Go!**

📧 **Gmail:**
- Status: ✅ Connected
- Account: amanethmeis@gmail.com
- Unread emails: 5
- Last check: Just now
- Issues: None

💬 **Telegram:**
- Status: ✅ Connected
- Bot: My Email Assistant (@MyEmailBot)
- Chat ID: 7596520776 (Your personal chat)
- Last message: 2 hours ago
- Issues: None

🤖 **Groq AI:**
- Status: ✅ Ready
- Model: Llama 3.3 70B Versatile
- Cost per email: $0.001
- Issues: None

🎯 **Overall:** Everything is working perfectly!

Next scheduled digest: 7:00 AM tomorrow (2026-03-28)
```

---

## Example 10: Complex Request with Multiple Tools

### You Ask:
```
I'm going into a 2-hour meeting. Can you:
1. Get my urgent emails
2. Send important ones to Telegram
3. Let me know if anything critical arrives while I'm in the meeting
```

### Claude Does:
```
I'll prepare you for the meeting.

[Step 1] Checking urgent emails...
[Calling tool: check_emails()]

[Step 2] Sending to Telegram...
[Calling tool: send_telegram_message() for each urgent]

[Step 3] Setting up monitoring...
I'll check every 10 minutes while you're in the meeting.
```

### You Get:
```
✅ **Meeting Prep Complete!**

**Your Urgent Emails (sent to Telegram):**
- Security alert from Google
- AWS billing notification

**Telegram Summary:**
3 messages sent with urgent email summaries

**Monitoring Active:**
I'll check your emails every 10 minutes.
If anything URGENT arrives, I'll alert you on Telegram.

**While You're Away:**
Time: Meeting duration (2 hours)
Check frequency: Every 10 minutes
Alert type: Urgent only (no interruption for important)
Timeout: 2 hours 15 minutes

You can focus on your meeting. Your phone will buzz if something critical arrives.
```

---

## Example 11: Productivity Integration

### You Ask:
```
Based on my urgent emails, create a priority list for today.
```

### Claude Does:
```
Let me analyze your urgent emails and create priorities.
[Calling tool: get_urgent_summary()]
[Processing into tasks...]
```

### You Get:
```
📋 **TODAY'S PRIORITY LIST**

**🔴 CRITICAL (Do First - Next 1 hour):**
1. Verify Google account security
   └─ Time: 15 minutes
   └─ From: Security alert
   └─ Action: Click Google link → Review recent activity
   
2. Approve AWS charge
   └─ Time: 5 minutes
   └─ From: AWS billing alert
   └─ Action: Check AWS console → Approve or dispute
   
3. Accept meeting invite
   └─ Time: 2 minutes
   └─ From: Calendar
   └─ Action: Open Slack → Confirm attendance

**🟡 IMPORTANT (Next 2-4 hours):**
4. Review invoice
5. Respond to team message

**🟢 CAN WAIT (Tomorrow okay):**
6. Newsletter content
7. Promotional emails (archive)

**⏱️ TIME ESTIMATE:**
- Critical: 22 minutes
- Important: 30 minutes
- Total: ~1 hour

**💡 Suggestion:**
Do critical tasks by 11 AM, then focus on project work.
```

---

## Tips for Best Results

### 1. Be Specific
✅ **Good:** "What urgent emails do I have from my boss?"
❌ **Vague:** "Check emails"

### 2. Ask Follow-ups
✅ **Good:** First ask summary, then ask to analyze, then send to Telegram
❌ **Poor:** Try to do everything at once

### 3. Use Context
✅ **Good:** "I'm about to leave my office. Alert me on Telegram if anything urgent arrives."
❌ **Poor:** "Send telegram"

### 4. Chain Requests
```
User: Check my emails
Claude: Shows summary

User: Send urgent ones to Telegram
Claude: Sends them

User: Set up monitoring for next 2 hours
Claude: Activates real-time monitoring
```

---

## Advanced Patterns

### Pattern 1: Daily Briefing
```
Every morning, ask Claude:
"My email briefing - urgent items, important items, and what to do today"
```

### Pattern 2: While Traveling
```
"Monitor my emails and alert to Telegram if anything urgent. 
I'll be traveling for 4 hours."
```

### Pattern 3: Before Vacation
```
"Summarize all important emails from the past week.
I'm going on vacation tomorrow."
```

### Pattern 4: Post-Meeting
```
"What arrived while I was in the meeting? 
Anything urgent I should know?"
```

---

## What Claude Can't Do (Limitations)

❌ **Cannot:**
- Automatically reply to emails
- Delete or archive emails
- Create email filters
- Access calendar details beyond emails
- Read attachments (currently)
- Modify email rules

✅ **Can:**
- Read and summarize emails
- Classify by priority
- Send alerts to Telegram
- Monitor for urgent emails
- Analyze suspicious emails
- Provide recommendations

---

**Next: Set up your first Email Bridge connection!** 📧

