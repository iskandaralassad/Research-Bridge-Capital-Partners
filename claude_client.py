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

WEB_SEARCH_TOOL = {"type": "web_search_20250305", "name": "web_search"}


def generate_report(system_prompt: str, user_prompt: str, max_search_turns: int = 6) -> str:
    """
    Calls Claude with the web_search tool enabled, handles the multi-turn
    tool-use loop server-side (web_search is executed by Anthropic, not by us),
    and returns the concatenated text output.
    """
    messages = [{"role": "user", "content": user_prompt}]

    for _ in range(max_search_turns):
        payload = {
            "model": MODEL_NAME,
            "max_tokens": MAX_TOKENS,
            "system": system_prompt,
            "messages": messages,
            "tools": [WEB_SEARCH_TOOL],
        }
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=180)
        resp.raise_for_status()
        data = resp.json()

        # web_search is a server-executed tool: Anthropic runs the search and
        # returns the results inline. We just need to keep sending the
        # conversation back if Claude wants to keep searching (stop_reason
        # "tool_use" would only appear for client-executed tools; for
        # server tools we typically get "end_turn" once Claude is done).
        stop_reason = data.get("stop_reason")
        messages.append({"role": "assistant", "content": data["content"]})

        if stop_reason != "tool_use":
            break

        # Fallback safety: if a client-side tool_use block ever appears
        # (shouldn't happen with web_search), stop the loop gracefully.
        time.sleep(1)

    text_parts = [
        block["text"] for block in data["content"] if block.get("type") == "text"
    ]
    return "\n".join(text_parts).strip()
