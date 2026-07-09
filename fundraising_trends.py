"""
Runs the weekly Fundraising Trends report (family offices, fund-of-funds,
DFIs, sovereign wealth funds, and other allocators) and emails it to the
configured recipient group. Intended to run every Friday.

Run manually:  python fundraising_trends.py
Scheduled via: .github/workflows/friday-newsletters.yml
"""

from datetime import date
from prompts import fundraising_trends_prompt
from claude_client import generate_report
from email_sender import send_report


def main():
    today = date.today()
    system, user = fundraising_trends_prompt(today)
    html_body = generate_report(system, user)

    date_str = today.strftime("%B %d, %Y")
    send_report(
        subject=f"Bridge Capital Partners — Fundraising Trends — Week of {date_str}",
        subtitle="Fundraising Trends — Allocators",
        date_str=date_str,
        html_body=html_body,
    )


if __name__ == "__main__":
    main()
