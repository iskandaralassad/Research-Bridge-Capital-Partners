"""
Runs the weekly Investment Trends report (AI company funding rounds) and
emails it to the configured recipient group. Intended to run every Friday.

Run manually:  python investment_trends.py
Scheduled via: .github/workflows/friday-newsletters.yml
"""

from datetime import date
from prompts import investment_trends_prompt
from claude_client import generate_report
from email_sender import send_report


def main():
    today = date.today()
    system, user = investment_trends_prompt(today)
    html_body = generate_report(system, user)

    date_str = today.strftime("%B %d, %Y")
    send_report(
        subject=f"Bridge Capital Partners — Investment Trends (AI) — Week of {date_str}",
        subtitle="Investment Trends — AI Deals",
        date_str=date_str,
        html_body=html_body,
    )


if __name__ == "__main__":
    main()
