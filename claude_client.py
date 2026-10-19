"""
Thin wrapper around the Anthropic Messages API that:
- enables the native web_search tool
- runs a research phase (tool-use loop) and then a final write phase
- returns only the finished HTML report
"""

import time
import requests
from config import ANTHROPIC_API_KEY, MODEL_NAME, MAX_TOKENS

API_URL = "https://api.anthropic.com/v1/messages"

HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 10,  # cap searches per request; pause_turn lets Claude continue after
}

# (connect timeout, read timeout) in seconds.
REQUEST_TIMEOUT = (15, 600)
MAX_RETRIES = 3
RETRYABLE_STATUS = {429, 500, 502, 503, 504, 529}


def _post_with_retry(payload: dict) -> requests.Response:
    """POST to the API, retrying on timeouts, connection errors and transient
    HTTP errors (429/5xx/529) with backoff."""
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=REQUEST_TIMEOUT)
            if resp.status_code in RETRYABLE_STATUS and attempt < MAX_RETRIES:
                wait = 20 * attempt
                print(f"Transient API error {resp.status_code}; retry {attempt}/{MAX_RETRIES - 1} in {wait}s")
                time.sleep(wait)
                continue
            return resp
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as exc:
            last_exc = exc
            if attempt == MAX_RETRIES:
                break
            wait = 20 * attempt
            print(f"{type(exc).__name__}; retry {attempt}/{MAX_RETRIES - 1} in {wait}s")
            time.sleep(wait)
    raise last_exc


def generate_report(system_prompt: str, user_prompt: str, max_search_turns: int = 10) -> str:
    """
    Two phases:
    1) RESEARCH: Claude searches the web (server-side web_search). We keep
       resuming the conversation while stop_reason is tool_use / pause_turn.
    2) WRITE: one final call with tools disabled (tool_choice=none) that asks
       Claude to write ONLY the finished HTML report from the research above.
    Only the text of that final call is returned, so no narration such as
    "I'll research..." and no half-written tables end up in the email.
    """
    messages = [{"role": "user", "content": user_prompt}]
    finished_naturally = False

    for turn in range(max_search_turns):
        payload = {
            "model": MODEL_NAME,
            "max_tokens": MAX_TOKENS,
            "system": system_prompt,
            "messages": messages,
            "tools": [WEB_SEARCH_TOOL],
        }
        resp = _post_with_retry(payload)
        if not resp.ok:
            print("Anthropic API error response body:", resp.text)
        resp.raise_for_status()
        data = resp.json()

        stop_reason = data.get("stop_reason")
        print(f"Research turn {turn + 1}: stop_reason={stop_reason}")
        messages.append({"role": "assistant", "content": data["content"]})

        if stop_reason not in ("tool_use", "pause_turn"):
            finished_naturally = True
            break
        time.sleep(1)

    if not finished_naturally:
        print(f"NOTE: research hit max_search_turns={max_search_turns}; moving to final write step.")

    # Final write step: no more searching, just produce the report.
    messages.append({
        "role": "user",
        "content": (
            "Research is complete. Now write the FINAL report as specified, using only "
            "what you found above. Output ONLY the HTML report body, starting directly "
            "with the first section. No introduction, no commentary, no mention of "
            "searching. Include ALL sections, in order, even if a section has no items "
            "(say so plainly). Do not stop mid-table."
        ),
    })
    payload = {
        "model": MODEL_NAME,
        "max_tokens": MAX_TOKENS,
        "system": system_prompt,
        "messages": messages,
        "tools": [WEB_SEARCH_TOOL],
        "tool_choice": {"type": "none"},
    }
    resp = _post_with_retry(payload)
    if not resp.ok:
        print("Anthropic API error response body (final step):", resp.text)
    resp.raise_for_status()
    data = resp.json()
    print(f"Final write step: stop_reason={data.get('stop_reason')}")
    if data.get("stop_reason") == "max_tokens":
        print("WARNING: final report hit max_tokens and may be truncated.")

    html_body = "\n".join(
        b["text"] for b in data["content"] if b.get("type") == "text"
    ).strip()

    # Strip markdown code fences if the model wrapped the HTML.
    if html_body.startswith("```"):
        html_body = html_body.split("\n", 1)[-1]
        if html_body.rstrip().endswith("```"):
            html_body = html_body.rstrip()[:-3]
        html_body = html_body.strip()

    if not html_body:
        raise RuntimeError(
            "generate_report() produced an EMPTY report body in the final write "
            "step. Check the stop_reason lines above in this log."
        )

    return html_body
