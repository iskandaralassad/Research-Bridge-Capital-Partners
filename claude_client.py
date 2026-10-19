"""
Thin wrapper around the Anthropic Messages API that:
- enables the native web_search tool
- runs the tool-use loop until Claude returns a final text response
- concatenates all text blocks into a single HTML string
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

# (connect timeout, read timeout) in seconds. A single response with many web
# searches can take several minutes, so the read timeout must be generous.
REQUEST_TIMEOUT = (15, 600)
MAX_RETRIES = 3
RETRYABLE_STATUS = {429, 500, 502, 503, 504, 529}


def _post_with_retry(payload: dict) -> requests.Response:
    """POST to the API, retrying on timeouts, connection errors and transient
    HTTP errors (429/5xx/529) with exponential backoff."""
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


def generate_report(system_prompt: str, user_prompt: str, max_search_turns: int = 15) -> str:
    """
    Calls Claude with the web_search tool enabled, handles the multi-turn
    tool-use loop server-side (web_search is executed by Anthropic, not by us),
    and returns the concatenated text output.
    """
    messages = [{"role": "user", "content": user_prompt}]
    data = None

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
            # Print Anthropic's detailed error body before raising, so the
            # real cause (invalid model, bad request, rate limit, etc.)
            # shows up in the GitHub Actions log instead of just "400/429".
            print("Anthropic API error response body:", resp.text)
        resp.raise_for_status()
        data = resp.json()

        # web_search is a server-executed tool: Anthropic runs the search and
        # returns the results inline. We need to keep sending the conversation
        # back to let Claude continue in two cases: "tool_use" (Claude wants
        # to call another tool) and "pause_turn" (Claude paused mid-turn,
        # typically during a long-running server-side tool sequence like an
        # extended web_search session, and needs another request to resume
        # and finish). Only "end_turn" (and similar final reasons) mean
        # Claude is actually done and has written its final text.
        stop_reason = data.get("stop_reason")
        print(f"Turn {turn + 1}: stop_reason={stop_reason}")
        messages.append({"role": "assistant", "content": data["content"]})

        if stop_reason not in ("tool_use", "pause_turn"):
            break

        # Fallback safety: brief pause between continuation requests.
        time.sleep(1)
    else:
        # The loop ran out of turns while Claude was still trying to search —
        # the report is likely incomplete. Fail loudly instead of silently
        # sending a blank/partial email.
        print(
            f"WARNING: hit max_search_turns={max_search_turns} without Claude "
            "finishing. The report may be incomplete."
        )

    text_parts = [
        block["text"] for block in data["content"] if block.get("type") == "text"
    ]
    html_body = "\n".join(text_parts).strip()

    if not html_body:
        raise RuntimeError(
            "generate_report() produced an EMPTY report body. This usually means "
            "Claude ran out of search turns before writing the final summary, or "
            "returned only tool-use content with no text block. Raising an error "
            "here instead of sending a blank email — check the 'stop_reason' lines "
            "above in this log to see how far it got."
        )

    return html_body
