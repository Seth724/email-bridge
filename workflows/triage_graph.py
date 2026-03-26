"""
LangGraph Email Triage Workflow

Defines the state graph for email classification and routing.
Uses LangGraph for structured, debuggable workflows.
"""

from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import logging

logger = logging.getLogger(__name__)


# Define the state schema
class EmailState(TypedDict):
    """State for email processing workflow"""

    emails: List[dict]  # Raw email data
    classified_emails: List[dict]  # Classified results
    urgent_emails: List[dict]  # Filtered urgent emails
    important_emails: List[dict]  # Filtered important emails
    summary: str  # Generated summary
    send_telegram: bool  # Whether to send to Telegram


class EmailTriageWorkflow:
    """LangGraph-based email triage workflow"""

    def __init__(self, classifier):
        """
        Initialize workflow

        Args:
            classifier: EmailClassifier instance
        """
        self.classifier = classifier
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph"""

        # Create graph
        workflow = StateGraph(EmailState)

        # Add nodes
        workflow.add_node("classify_emails", self._classify_emails)
        workflow.add_node("filter_by_priority", self._filter_by_priority)
        workflow.add_node("generate_summary", self._generate_summary)
        workflow.add_node("decide_notification", self._decide_notification)

        # Add edges
        workflow.add_edge(START, "classify_emails")
        workflow.add_edge("classify_emails", "filter_by_priority")
        workflow.add_edge("filter_by_priority", "generate_summary")
        workflow.add_edge("generate_summary", "decide_notification")
        workflow.add_edge("decide_notification", END)

        # Compile
        return workflow.compile()

    def _classify_emails(self, state: EmailState) -> dict:
        """Classify all emails"""
        logger.info(f"Classifying {len(state['emails'])} emails...")

        classified = []
        for email in state["emails"]:
            result = self.classifier.classify_email(email)
            classified.append(result)

        return {"classified_emails": classified}

    def _filter_by_priority(self, state: EmailState) -> dict:
        """Filter emails by priority"""
        urgent = [
            e for e in state["classified_emails"] if e["category"] == "URGENT"
        ]
        important = [
            e for e in state["classified_emails"] if e["category"] == "IMPORTANT"
        ]

        logger.info(f"Found {len(urgent)} urgent, {len(important)} important emails")

        return {
            "urgent_emails": urgent,
            "important_emails": important,
        }

    def _generate_summary(self, state: EmailState) -> dict:
        """Generate summary text"""
        summary = "📧 **Email Briefing**\n\n"

        urgent = state["urgent_emails"]
        important = state["important_emails"]

        if urgent:
            summary += f"🚨 **URGENT** ({len(urgent)}):\n"
            for email in urgent:
                summary += f"• {email['email_subject']} (from {email['email_sender']})\n"
                summary += f"  _{email['summary']}_\n"
                summary += f"  **Action**: {email.get('action_needed', 'Review')}\n\n"

        if important:
            summary += f"📌 **IMPORTANT** ({len(important)}):\n"
            for email in important:
                summary += f"• {email['email_subject']} (from {email['email_sender']})\n"

        if not urgent and not important:
            summary += "✅ No urgent or important emails. All caught up!"

        return {"summary": summary}

    def _decide_notification(self, state: EmailState) -> dict:
        """Decide whether to send notification"""
        # Always send if there are urgent emails
        should_send = len(state["urgent_emails"]) > 0

        return {"send_telegram": should_send}

    def process_emails(self, emails: List[dict]) -> dict:
        """
        Process emails through the workflow

        Args:
            emails: List of raw email dictionaries

        Returns:
            Final state with classifications and summary
        """
        if not emails:
            logger.info("No emails to process")
            return {
                "emails": [],
                "classified_emails": [],
                "urgent_emails": [],
                "important_emails": [],
                "summary": "✅ No emails to process.",
                "send_telegram": False,
            }

        # Run workflow
        initial_state = {
            "emails": emails,
            "classified_emails": [],
            "urgent_emails": [],
            "important_emails": [],
            "summary": "",
            "send_telegram": False,
        }

        try:
            final_state = self.graph.invoke(initial_state)
            logger.info("Workflow completed successfully")
            return final_state

        except Exception as e:
            logger.error(f"Workflow error: {e}")
            # Return fallback
            return {
                "emails": emails,
                "classified_emails": [],
                "urgent_emails": [],
                "important_emails": [],
                "summary": f"⚠️ Error processing emails: {str(e)}",
                "send_telegram": False,
            }
