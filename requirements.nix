# Render Build & Run Configuration

# Use Python 3.11
pythonVersion: 3.11.0

# Install dependencies
install:
  - pip install -r requirements.txt
  - pip install -r requirements-audio.txt

# Start the webhook server
start: python webhook_server.py
