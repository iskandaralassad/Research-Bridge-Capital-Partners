"""
Central configuration for the Bridge Capital Partners Research Agent.
Edit this file to adjust recipients, model, and source preferences.
Sensitive values (API keys, email password) are read from environment
variables / GitHub Actions secrets — never hardcode them here.
"""

import os

# ---------------------------------------------------------------------------
# Anthropic API
# ---------------------------------------------------------------------------
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

# Check https://docs.claude.com/en/docs/about-claude/models for the current
# recommended model ID before deploying to production — model names are
# updated periodically.
MODEL_NAME = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = 8000

# ---------------------------------------------------------------------------
# Email (Gmail API + OAuth2)
# ---------------------------------------------------------------------------
# Used because Google Workspace admin has disabled App Passwords for this
# account. Requires a Google Cloud project with the Gmail API enabled and an
# OAuth2 Desktop-app client — see README section "Gmail API setup".
GMAIL_SENDER = os.environ["EMAIL_ADDRESS"]              # e.g. alexandre.leao@bdcp.com.br
GMAIL_CLIENT_ID = os.environ["GMAIL_CLIENT_ID"]
GMAIL_CLIENT_SECRET = os.environ["GMAIL_CLIENT_SECRET"]
GMAIL_REFRESH_TOKEN = os.environ["GMAIL_REFRESH_TOKEN"]
FROM_NAME = "Bridge Capital Partners Research"

# Comma-separated list of recipients, provided as a single secret, e.g.:
# "partner1@bridgecapital.com,partner2@bridgecapital.com"
RECIPIENTS = [
    addr.strip()
    for addr in os.environ.get("EMAIL_RECIPIENTS", "").split(",")
    if addr.strip()
]

# ---------------------------------------------------------------------------
# Source guidance (used inside the prompts to steer web_search)
# ---------------------------------------------------------------------------
PRIMARY_NEWS_SOURCES = [
    "Bloomberg", "Reuters", "Financial Times", "The Wall Street Journal",
    "The Economist", "CNBC", "Axios Pro Rata", "TechCrunch", "The Information",
    "Fortune", "Business Insider", "Forbes", "Sifted", "PitchBook News",
    "The Verge", "Ars Technica", "Wired", "Semafor Tech", "Import AI",
    "The Batch (DeepLearning.AI)",
]

INVESTMENT_TRENDS_SOURCES = [
    "TechCrunch", "The Information", "PitchBook", "Crunchbase News",
    "Axios Pro Rata", "Sifted", "Fortune Term Sheet", "Bloomberg Technology",
    "Reuters Technology", "CB Insights",
]

FUNDRAISING_TRENDS_SOURCES = [
    "Institutional Investor", "Private Equity International", "Preqin",
    "Global SWF", "Family Capital", "AVCJ", "Bloomberg", "Reuters",
    "Financial Times (FT Alphaville / FT Wealth)", "Devex (for DFIs)",
]

COMPANY_NAME = "Bridge Capital Partners"
