from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="email-bridge",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered email triage system with Telegram notifications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/email-bridge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "python-dotenv>=1.0.0",
        "groq>=0.9.0",
        "langgraph>=0.2.50",
        "langchain>=0.3.0",
        "langchain-groq>=0.2.0",
        "langsmith>=0.3.0",
        "imaplib2>=3.0.7",
        "python-telegram-bot>=21.0",
        "fastmcp>=0.5.0",
        "APScheduler>=3.11.0",
        "pydantic>=2.0.0",
        "beautifulsoup4>=4.12.0",
        "html2text>=2024.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.25.0",
            "black>=24.0.0",
            "ruff>=0.8.0",
        ],
        "remote": [
            "uvicorn>=0.34.0",
            "fastapi>=0.115.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "email-bridge=standalone.bot:check_and_notify",
            "email-bridge-schedule=standalone.scheduler:main",
            "email-bridge-mcp=mcp.server:main",
        ],
    },
)
