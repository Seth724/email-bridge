# Email Bridge - Project Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMAIL BRIDGE SYSTEM                           │
│                                                                  │
│  ┌────────────┐      ┌─────────────┐      ┌────────────┐       │
│  │   Gmail    │─────▶│  LangGraph  │─────▶│  Telegram  │       │
│  │   IMAP     │      │ Classifier  │      │   Sender   │       │
│  │            │      │  (Groq AI)  │      │            │       │
│  └────────────┘      └─────────────┘      └────────────┘       │
│       ▲                    │                    │               │
│       │                    ▼                    │               │
│       │           ┌─────────────────┐          │               │
│       └───────────│   LangSmith     │◀─────────┘               │
│                   │   (Tracing)     │                          │
│                   └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘

                    DEPLOYMENT OPTIONS
┌──────────────────┬──────────────────┬──────────────────┐
│  Standalone Bot  │  MCP Local       │  MCP Remote      │
│  (Scheduler)     │  (Claude Desktop)│  (Railway/Render)│
└──────────────────┴──────────────────┴──────────────────┘
```

## Data Flow

```
1. Gmail IMAP Fetch
   ↓
2. Email Classification (Groq LLM)
   ↓
3. Priority Filtering (LangGraph)
   ↓
4. Summary Generation
   ↓
5. Telegram Notification
   ↓
6. LangSmith Tracing (Optional)
```

## Component Breakdown

### Core Module (`core/`)

```
core/
├── gmail.py           # IMAP email fetching
│   ├── GmailFetcher class
│   ├── fetch_unread_emails()
│   ├── mark_as_read()
│   └── _get_email_body()
│
├── classifier.py      # AI classification
│   ├── EmailClassifier class
│   ├── classify_email()
│   ├── classify_batch()
│   └── _get_system_prompt()
│
└── telegram.py        # Telegram notifications
    ├── TelegramSender class
    ├── send_message()
    ├── send_urgent_alert()
    └── send_daily_digest()
```

### Workflows Module (`workflows/`)

```
workflows/
└── triage_graph.py    # LangGraph workflow
    ├── EmailState (TypedDict)
    ├── EmailTriageWorkflow class
    ├── _classify_emails()
    ├── _filter_by_priority()
    ├── _generate_summary()
    └── _decide_notification()
```

### Deployment Modes

```
standalone/
├── bot.py             # One-time email check
│   └── check_and_notify()
│
└── scheduler.py       # APScheduler automation
    └── main()  # Runs daily at 7 AM

mcp/
└── server.py          # FastMCP server
    ├── check_emails()      # Tool
    ├── get_urgent_summary()# Tool
    ├── send_telegram_message() # Tool
    ├── test_connection()   # Tool
    └── classify_email_sample() # Tool
```

## Email Classification Flow

```
                    Incoming Email
                         │
                         ▼
        ┌────────────────────────────────┐
        │  Groq LLM (llama-3.3-70b)      │
        │  Analyzes:                     │
        │  - Subject line                │
        │  - Sender                      │
        │  - Body content                │
        └────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │  Classification Result         │
        │  {                             │
        │    category: URGENT/IMPORTANT/ │
        │                NORMAL/SPAM     │
        │    confidence: 0.0-1.0         │
        │    reasoning: "..."            │
        │    action_needed: "..."        │
        │    summary: "..."              │
        │  }                             │
        └────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
   URGENT/IMPORTANT                  NORMAL/SPAM
        │                                 │
        ▼                                 ▼
  Send Telegram                      Skip (no alert)
  + Daily Digest
```

## Technology Stack

```
┌─────────────────────────────────────────────────┐
│  Layer              │  Technology               │
├─────────────────────────────────────────────────┤
│  AI/LLM             │  Groq API (Llama 3.3)     │
│  Workflow           │  LangGraph                │
│  Tracing            │  LangSmith                │
│  Email Protocol     │  IMAP (Gmail)             │
│  Notification       │  Telegram Bot API         │
│  MCP Framework      │  FastMCP                  │
│  Scheduling         │  APScheduler / GitHub     │
│  Deployment         │  Railway / Render         │
│  Language           │  Python 3.10+             │
└─────────────────────────────────────────────────┘
```

## API Integrations

### 1. Groq API (Free Tier)
- **Purpose**: LLM inference for email classification
- **Model**: `llama-3.3-70b-versatile` (or `mixtral-8x7b-32768`)
- **Limit**: 500 requests/day free
- **Cost**: $0 for personal use

### 2. Gmail IMAP (Free)
- **Purpose**: Fetch unread emails
- **Auth**: App Password (no OAuth needed)
- **Limit**: Unlimited
- **Cost**: $0

### 3. Telegram Bot API (Free)
- **Purpose**: Send notifications
- **Limit**: Unlimited messages
- **Cost**: $0

### 4. LangSmith (Free Tier)
- **Purpose**: Trace AI decisions
- **Limit**: 50K traces/month
- **Cost**: $0 for development

## Deployment Architectures

### Architecture 1: Standalone Bot (Local)

```
┌──────────────────────────────────────┐
│  User's Computer                     │
│  ┌────────────────────────────────┐  │
│  │  Python Script                 │  │
│  │  ┌──────────┐  ┌──────────┐   │  │
│  │  │ Gmail    │  │ Groq     │   │  │
│  │  │ IMAP     │  │ API      │   │  │
│  │  └──────────┘  └──────────┘   │  │
│  │         │             │        │  │
│  │         └──────┬──────┘        │  │
│  │                ▼               │  │
│  │        ┌──────────────┐       │  │
│  │        │ LangGraph    │       │  │
│  │        │ Workflow     │       │  │
│  │        └──────────────┘       │  │
│  │                │               │  │
│  │                ▼               │  │
│  │        ┌──────────────┐       │  │
│  │        │ Telegram     │       │  │
│  │        │ Sender       │       │  │
│  │        └──────────────┘       │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
           │
           ▼
    ┌──────────────┐
    │   Telegram   │
    │   (Phone)    │
    └──────────────┘
```

### Architecture 2: MCP Local (Claude Desktop)

```
┌──────────────────────────────────────┐
│  User's Computer                     │
│  ┌────────────────────────────────┐  │
│  │  Claude Desktop                │  │
│  │         │                      │  │
│  │         ▼                      │  │
│  │  ┌──────────────────────────┐  │  │
│  │  │  MCP Client              │  │  │
│  │  └──────────────────────────┘  │  │
│  │         │                      │  │
│  │         ▼                      │  │
│  │  ┌──────────────────────────┐  │  │
│  │  │  Email Bridge MCP        │  │  │
│  │  │  (server.py)             │  │  │
│  │  └──────────────────────────┘  │  │
│  │         │                      │  │
│  │         ▼                      │  │
│  │  Gmail + Groq + Telegram       │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

### Architecture 3: MCP Remote (Cloud)

```
┌──────────────────┐         ┌──────────────────┐
│  User's Computer │         │   Railway Cloud  │
│  ┌────────────┐  │         │  ┌────────────┐  │
│  │  Claude    │  │  HTTP   │  │  Email     │  │
│  │  Desktop   │──┼─────────┼─▶│  Bridge    │  │
│  └────────────┘  │  SSE    │  │  MCP       │  │
│                  │         │  └────────────┘  │
│                  │         │         │        │
│                  │         │         ▼        │
│                  │         │  Gmail + Groq    │
└──────────────────┘         └──────────────────┘
           │
           ▼
    ┌──────────────┐
    │   Telegram   │
    └──────────────┘
```

## Email Categories

| Category | Trigger | Notification | Example |
|----------|---------|--------------|---------|
| **URGENT** | Immediate (sound) | Instant alert | Flight delays, job offers, bank fraud alerts |
| **IMPORTANT** | Silent | Daily digest | Meeting invites, project updates |
| **NORMAL** | None | Skipped | Newsletters, notifications |
| **SPAM** | None | Deleted | Promotional spam, phishing |

## Configuration Files

```
.env                    # Environment variables
requirements.txt        # Python dependencies
setup.py               # Package configuration
claude_desktop_config.json  # MCP client config (user-side)
railway.json           # Railway deployment config
.github/workflows/     # GitHub Actions automation
```

## Security Considerations

```
✅ App Passwords (not main Gmail password)
✅ Environment variables (not hardcoded)
✅ .gitignore for .env files
✅ No email content stored locally
✅ HTTPS for all API calls
✅ LangSmith tracing (optional, can be disabled)
```

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Email fetch time | ~1-2 seconds per email |
| Classification time | ~0.5-1 second per email (Groq is fast!) |
| Telegram send time | ~0.2 seconds |
| Total for 10 emails | ~15-20 seconds |
| Memory usage | ~50-100 MB |
| CPU usage | Low (mostly I/O bound) |

## Cost Breakdown (Monthly)

| Service | Free Tier | Personal Use | Heavy Use |
|---------|-----------|--------------|-----------|
| Groq API | 500 req/day | $0 | $0-10 |
| Gmail IMAP | Unlimited | $0 | $0 |
| Telegram | Unlimited | $0 | $0 |
| LangSmith | 50K traces | $0 | $0-25 |
| Railway | $5 credit | $0 | $0-5 |
| **TOTAL** | | **$0** | **$0-40** |

## Extensibility Points

```
1. Add more LLM providers (Ollama, OpenAI, Anthropic)
2. Support more email providers (Outlook, Yahoo, custom IMAP)
3. Add more notification channels (WhatsApp, Slack, Email)
4. Custom classification categories
5. Interactive Telegram commands (/archive, /snooze, /reply)
6. Web dashboard (Streamlit/Gradio)
7. Database for email history (SQLite/PostgreSQL)
8. Vector search for email similarity
```

## Testing Strategy

```
tests/
├── test_classifier.py   # Unit tests for AI classification
├── test_telegram.py     # Integration tests for Telegram
├── test_gmail.py        # Integration tests for Gmail (optional)
└── test_workflow.py     # End-to-end workflow tests

Run: pytest tests/ -v
```

## Monitoring & Observability

```
1. LangSmith Traces
   - See why emails were classified a certain way
   - Debug AI decision-making

2. Application Logs
   - Python logging to console/file
   - Log levels: INFO, WARNING, ERROR

3. Telegram Error Alerts
   - Bot sends error notifications to user
   - Includes stack traces for debugging

4. Health Checks
   - /health endpoint (for remote deployment)
   - test_connection() tool
```

## Future Roadmap

```
Phase 1 (Current): Core functionality
├── Gmail IMAP fetching
├── Groq AI classification
├── Telegram notifications
└── LangGraph workflow

Phase 2 (Next): Enhanced features
├── Interactive Telegram buttons
├── Email archiving from Telegram
├── Custom classification rules
└── Multi-account support

Phase 3 (Advanced): AI improvements
├── Fine-tuned classification model
├── Learning from user feedback
├── Smart snooze suggestions
└── Auto-draft replies

Phase 4 (Enterprise): Team features
├── Shared inbox support
├── Team notification routing
├── Analytics dashboard
└── SLA monitoring
```
