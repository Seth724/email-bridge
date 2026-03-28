# Procfile for deployment platforms (Railway, Render, Heroku)

# Web server - handles both MCP and webhook on same port
web: python webhook_server.py

# Alternative: Run only webhook server (MCP runs separately)
# webhook: python webhook_server.py

# For Railway with automatic webhook registration:
# Set DEPLOYMENT_MODE=remote and PUBLIC_URL in environment
