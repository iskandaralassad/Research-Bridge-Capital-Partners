"""
Runs the Daily News briefing: searches today's major business/investing/tech
news and emails the summary to the configured recipient group.

Run manually:  python daily_news.py
Scheduled via: .github/workflows/daily-news.yml
"""

from datetime import date
from prompts import daily_news_prompt
from claude_client import generate_report
from email_sender import send_report


def main():
    today = date.today()
    system, user = daily_news_prompt(today)
    html_body = generate_report(system, user)

    date_str = today.strftime("%B %d, %Y")
    send_report(
        subject=f"Bridge Capital Partners — Daily News — {date_str}",
        subtitle="Daily News",
        date_str=date_str,
        html_body=html_body,
    )


if __name__ == "__main__":
    main()
