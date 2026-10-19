"""
Runs the DAILY Investment Trends report (AI companies: closed rounds, open
rounds, announced upcoming rounds, SAFE raises in the last 6 months, tender
offers) and emails it to the configured recipient group.

Runs each morning and covers the PREVIOUS day (plus overnight news).

Run manually:  python investment_trends.py
Scheduled via: .github/workflows/daily-investment-trends.yml
"""

from datetime import date, timedelta
from prompts import investment_trends_prompt
from claude_client import generate_report
from email_sender import send_report


def main():
    target_day = date.today() - timedelta(days=1)
    system, user = investment_trends_prompt(target_day)
    html_body = generate_report(system, user)

    date_str = target_day.strftime("%B %d, %Y")
    send_report(
        subject=f"Bridge Capital Partners — Investment Trends (AI) — Daily — {date_str}",
        subtitle="Investment Trends — Daily AI Deals",
        date_str=date_str,
        html_body=html_body,
    )


if __name__ == "__main__":
    main()
