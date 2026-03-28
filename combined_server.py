"""
Combined Server for Render Deployment

Runs both:
1. FastMCP server (for Claude Desktop connection)
2. Webhook server (for Telegram button callbacks)

Both run on the same port using FastAPI.
"""

import os
import sys
import logging
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def run_webhook_server():
    """Run webhook server in background thread"""
    import uvicorn
    
    # Import app from webhook_server module
    from webhook_server import app
    
    # Webhook runs on same port, different path
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting webhook server on {host}:{port}/webhook")
    
    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as e:
        logger.error(f"Webhook server error: {e}")


def run_mcp_server():
    """Run FastMCP server"""
    from mcp.server import mcp
    
    transport = os.getenv("MCP_TRANSPORT", "streamable-http").lower()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    path = os.getenv("MCP_PATH", "/mcp")
    
    logger.info(f"Starting FastMCP server ({transport}) on {host}:{port}{path}")
    
    try:
        mcp.run(transport=transport, host=host, port=port, path=path)
    except Exception as e:
        logger.error(f"MCP server error: {e}")


def main():
    """Run both servers"""
    logger.info("=" * 60)
    logger.info("Email Bridge - Combined Server")
    logger.info("=" * 60)
    
    # Start webhook server in background thread
    webhook_thread = threading.Thread(target=run_webhook_server, daemon=True)
    webhook_thread.start()
    
    # Run MCP server in main thread
    run_mcp_server()


if __name__ == "__main__":
    main()
