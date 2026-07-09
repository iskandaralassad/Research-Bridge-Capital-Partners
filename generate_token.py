"""
ONE-TIME SETUP SCRIPT — run this locally (on your own computer, not in
GitHub Actions) to generate the Gmail refresh_token needed by email_sender.py.

Prerequisites (see README.md "Gmail API setup"):
- A Google Cloud project with the Gmail API enabled.
- An OAuth2 "Desktop app" client created in that project, with its
  client_id and client_secret downloaded as a JSON file (or just copy the
  two values below).

Usage:
    pip install requests
    python generate_token.py

This will:
1. Print a URL — open it in your browser and log in as
   alexandre.leao@bdcp.com.br (the sending account).
2. Grant permission ("Send email on your behalf").
3. Google will redirect to a localhost URL that won't load (that's expected,
   it's a "no listener" desktop-app flow) — copy the "code" value from that
   URL's address bar.
4. Paste it back into this script's prompt.
5. The script prints your refresh_token — copy it into the GitHub secret
   GMAIL_REFRESH_TOKEN.
"""

import requests
import urllib.parse

# --- Fill these in from your Google Cloud OAuth2 client -------------------
CLIENT_ID = "PASTE_YOUR_CLIENT_ID_HERE"
CLIENT_SECRET = "PASTE_YOUR_CLIENT_SECRET_HERE"
# ---------------------------------------------------------------------------

REDIRECT_URI = "http://localhost"
SCOPE = "https://www.googleapis.com/auth/gmail.send"

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def main():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",   # forces Google to always return a refresh_token
    }
    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    print("\n1. Open this URL in your browser and log in as the SENDING account:\n")
    print(url)
    print(
        "\n2. After granting permission, the browser will try to load a "
        "localhost page and FAIL to connect — this is expected."
    )
    print(
        "3. Copy the value of the 'code' parameter from that broken page's "
        "address bar (everything after 'code=' and before the next '&', if any).\n"
    )

    code = input("Paste the code here: ").strip()

    resp = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    print("\n--- SUCCESS ---")
    print("Save this refresh_token as the GitHub secret GMAIL_REFRESH_TOKEN:\n")
    print(data["refresh_token"])
    print(
        "\nAlso save GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET (the values you "
        "filled in above) as GitHub secrets with those exact names."
    )


if __name__ == "__main__":
    main()
