"""
Runs the Daily News briefing: runs each morning and searches the PREVIOUS
day's major AI news, then emails the summary to the configured recipient
group.

Run manually:  python daily_news.py
Scheduled via: .github/workflows/daily-news.yml (runs ~7:00 AM Brasília time)
"""

from datetime import date, timedelta
from prompts import daily_news_prompt
from claude_client import generate_report
from email_sender import send_report


def main():
    # This runs in the morning, so the "day's news" we want is yesterday's —
    # today's news hasn't happened yet.
    target_day = date.today() - timedelta(days=1)
    system, user = daily_news_prompt(target_day)
    html_body = generate_report(system, user)

    date_str = target_day.strftime("%B %d, %Y")
    send_report(
        subject=f"Bridge Capital Partners — Daily News — {date_str}",
        subtitle="Daily News",
        date_str=date_str,
        html_body=html_body,
    )


if __name__ == "__main__":
    main()
