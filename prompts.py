"""
Prompt templates for each of the three newsletters.
Each function returns a (system_prompt, user_prompt) tuple ready to be sent
to the Claude API along with the web_search tool.

Design notes:
- Prompts instruct Claude to actually use web_search to find real, current
  articles (not to rely on memory), and to only cite links it retrieved via
  search.
- Output is requested as ready-to-send inline-styled HTML (email-safe),
  so the script can drop it straight into the email template body.
"""

from datetime import date
from config import (
    COMPANY_NAME,
    PRIMARY_NEWS_SOURCES,
    INVESTMENT_TRENDS_SOURCES,
    FUNDRAISING_TRENDS_SOURCES,
)

HTML_OUTPUT_RULES = """
FORMAT RULES:
- Output ONLY the inner HTML body content (no <html>, <head>, or <body> tags).
- Use inline CSS only (email clients strip <style> blocks): e.g.
  <p style="font-family:Georgia,serif;font-size:15px;color:#1a1a1a;line-height:1.5;">
- Use <h2 style="..."> for section headers, <h3 style="..."> for sub-items,
  <ul>/<li> for lists, and <a href="URL" style="color:#0a5a8c;">text</a> for links.
- Every factual claim about a specific news item MUST be backed by a real link
  you found via web_search. Never fabricate a URL, company name, dollar figure,
  or valuation. If a data point is genuinely unavailable, write "NA" — do not guess.
- Do not include a top-level title/logo — that is added by the email template.
- Keep prose tight and scannable; prefer bullets over long paragraphs.
"""


def daily_news_prompt(target_date: date | None = None):
    d = (target_date or date.today()).strftime("%B %d, %Y")
    system = (
        f"You are the research analyst for {COMPANY_NAME}, an investment management firm. "
        "You produce a rigorous, factual end-of-day AI-focused news briefing for the firm's "
        "partners. You MUST use the web_search tool extensively to find real, dated articles "
        f"published on {d}. Do not rely on prior knowledge for facts, figures, or links."
    )
    user = f"""
Build the Daily News briefing covering {d}. This briefing is EXCLUSIVELY focused on
artificial intelligence — do not include general business/market news unless it is
directly about AI (e.g., an AI-exposed public company's earnings, a macro event driven by
AI capex, etc.).

Search major global media outlets — prioritize: {", ".join(PRIMARY_NEWS_SOURCES)} —
plus any other reputable outlet (including specialized AI/tech press) with important
AI-related news from {d}.

Cover, in this order:
1. "AI Markets & Public Companies" — stock moves, earnings, or guidance from AI-exposed
   public companies (chipmakers, hyperscalers, AI software/model companies, etc.), and any
   macro news specifically tied to AI capex/demand.
2. "AI Corporate & Strategic Moves" — major AI-related M&A, partnerships, product launches,
   leadership changes, or enterprise deployments.
3. "AI Investing & Private Markets" — notable AI-related VC/PE/growth deals, fund closes,
   or major LP news announced on {d} (this is a quick daily pulse; the deep weekly dive on
   AI deals lives in the separate Investment Trends report).
4. "AI Policy & Regulation" — governmental, regulatory, or geopolitical news affecting AI
   (export controls, AI safety regulation, antitrust actions, etc.).
5. "Worth Watching" — 2-4 bullets on emerging AI stories that may develop further.

For each item: 1-2 sentence summary + the source name + a working hyperlink to the
original article (found via web_search — verify it is a real URL).

End with a short "Editor's Note" (2-3 sentences) synthesizing the overall tone of that day
in AI specifically (sentiment, dominant narrative, what mattered most).

{HTML_OUTPUT_RULES}
"""
    return system, user


def investment_trends_prompt(week_ending: date | None = None):
    d = (week_ending or date.today()).strftime("%B %d, %Y")
    system = (
        f"You are the research analyst for {COMPANY_NAME}. You produce a weekly AI investment "
        "trends report for the firm's partners, tracking capital deployed into AI companies. "
        "You MUST use web_search extensively to find real deals announced THIS WEEK. "
        "Never fabricate deal terms — if a figure (amount, valuation) is not disclosed "
        "publicly, write NA rather than estimating. In addition to CLOSED deals, you also "
        "surface companies reportedly CURRENTLY RAISING (open, not-yet-closed rounds) based "
        "on news coverage, funding databases, and credible chatter (e.g., Crunchbase, "
        "PitchBook, TechCrunch 'is raising' reports, founder/investor social posts, forum "
        "discussions) — always distinguish clearly between closed and open rounds, and label "
        "open-round information as unconfirmed/reported when it is not yet officially announced. "
        "You also track OPEN TENDER OFFERS — secondary liquidity events where existing "
        "shareholders/employees of private AI companies can sell shares (company-run tenders, "
        "or via platforms like Forge Global, EquityZen, Nasdaq Private Market) — distinct from "
        "primary funding rounds."
    )
    user = f"""
Build the weekly Investment Trends report for the week ending {d}, focused exclusively on
AI-related company investments (equity funding rounds, not M&A).

Search sources such as: {", ".join(INVESTMENT_TRENDS_SOURCES)}, and any other reputable
outlet or press release covering this week's AI funding announcements.

Structure the report as:

1. "This Week's AI Deals" — a table (use an HTML <table> with inline-styled cells) with
   columns: Company | Investors/Funds | Amount Invested | Valuation | Stage. Use "NA" for
   any missing field. Include as many verified deals as you can find (aim for at least
   8-15 if available), covering a range of deal sizes and geographies, not just mega-rounds.
   Only include CLOSED/announced rounds here.

2. "Companies Currently Raising (Open Rounds)" — a separate table of AI companies reported
   to be actively fundraising RIGHT NOW but not yet closed/confirmed, sourced from funding
   databases (Crunchbase, PitchBook, CB Insights), tech press "is in talks to raise" /
   "is raising" articles, and credible forum/social chatter (e.g., a16z or founder posts,
   relevant subreddits, X/Twitter threads from reputable VCs or journalists). Columns:
   Company | Reported Target Amount | Reported Valuation | Stage | Source/Where Reported.
   Use "NA" for any missing field, and add a one-line note under the table making clear
   this information is unconfirmed/reported and should be verified before acting on it.
   If you cannot find credible open-round chatter this week, state that plainly instead of
   fabricating entries.

3. "Companies with Open Tender Offers" — a table of AI companies with an active or recently
   announced tender offer (a secondary sale process letting existing employees/early
   shareholders sell shares — NOT a new primary funding round). Include company-organized
   tenders and ones facilitated by secondary marketplaces (e.g., Forge Global, EquityZen,
   Nasdaq Private Market, or a named investor/consortium buying secondary shares). Columns:
   Company | Tender Price / Implied Valuation | Organizer/Platform | Window or Deadline (if
   known) | Source. Use "NA" for any missing field. If none are found this week, state that
   plainly rather than fabricating entries.

4. "Thesis Consolidation" — 3-6 bullets synthesizing the dominant investment theses this
   week (e.g., vertical AI agents, AI infrastructure/compute, enterprise AI tooling,
   robotics, etc.) based on the deals observed.

5. "Trend Shifts" — 2-4 bullets on what changed vs. recent weeks (e.g., valuations
   compressing/expanding in a subsector, new investor types entering, geographic shifts).

6. "Notable Statistics" — 3-5 bullets with concrete numbers (e.g., total weekly AI funding
   volume, share going to US vs. rest of world, median round size by stage) — only include
   numbers you can source; cite the source inline.

7. "Sources & Further Reading" — bullet list of links to: (a) the news articles for each
   deal/tender listed in any table above, and (b) 2-4 broader pieces (fund reports, partner
   interviews, market analyses) that illustrate where major funds say their investment
   theses are headed.

{HTML_OUTPUT_RULES}
"""
    return system, user


def fundraising_trends_prompt(week_ending: date | None = None):
    d = (week_ending or date.today()).strftime("%B %d, %Y")
    system = (
        f"You are the research analyst for {COMPANY_NAME}. You produce a weekly Fundraising "
        "Trends report tracking how capital allocators (not operating companies) are "
        "deploying capital. You MUST use web_search extensively to find real, dated news "
        "from this week. Never fabricate allocator names, figures, or fund names."
    )
    user = f"""
Build the weekly Fundraising Trends report for the week ending {d}.

Focus on CAPITAL ALLOCATORS — family offices, fund-of-funds, development finance
institutions (DFIs), sovereign wealth funds, endowments, pension funds, and similar LPs —
NOT operating companies raising venture rounds.

Search sources such as: {", ".join(FUNDRAISING_TRENDS_SOURCES)}, and any other reputable
outlet covering this week's allocator activity.

Structure the report as:

1. "Allocator Activity This Week" — bullet or table list of concrete news items: allocator
   name, type (family office / FoF / DFI / SWF / pension / endowment / other), what they
   committed to or announced (fund commitment, direct investment, new mandate, strategic
   partnership, etc.), amount (or NA if undisclosed), geography, and thesis/sector focus.

2. "Geographic Flows" — 3-5 bullets summarizing where capital is moving geographically this
   week (e.g., increased allocation to Southeast Asia, Gulf sovereign funds expanding into
   Europe, etc.), with sourced links.

3. "Thesis & Mandate Shifts" — 3-5 bullets on what themes allocators are favoring (private
   credit, AI infrastructure, climate/energy transition, secondaries, direct deals vs. fund
   commitments, etc.) and how this compares to recent weeks.

4. "Notable Statistics" — 3-5 sourced bullets with concrete numbers (e.g., total DFI
   commitments this week, SWF direct-deal volume, family office co-investment activity).

5. "Sources & Further Reading" — links to all news items cited above, plus 2-4 broader
   pieces (allocator surveys, Preqin/Global SWF type reports, LP sentiment pieces) useful for
   understanding where allocator trends are heading.

{HTML_OUTPUT_RULES}
"""
    return system, user
