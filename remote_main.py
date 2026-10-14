"""Remote-Start fuer intervals-icu-mcp mit GitHub-Login und Nutzer-Freigabeliste.

Fail-closed: Jede MCP-Nachricht wird abgewiesen, wenn kein gueltiger GitHub-Login
vorliegt oder der Login nicht in ALLOWED_GITHUB_USERS steht.
"""
import os
import sys


def need(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(f"Umgebungsvariable {name} fehlt.")
    return value


BASE_URL = need("BASE_URL").rstrip("/")
GITHUB_CLIENT_ID = need("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = need("GITHUB_CLIENT_SECRET")
JWT_SIGNING_KEY = need("JWT_SIGNING_KEY")
ALLOWED = {u.strip().lower() for u in need("ALLOWED_GITHUB_USERS").split(",") if u.strip()}
need("INTERVALS_ICU_API_KEY")
need("INTERVALS_ICU_ATHLETE_ID")
# Sicherheitsboden: keine Loesch-Werkzeuge registrieren, falls nicht anders gesetzt.
os.environ.setdefault("INTERVALS_ICU_DELETE_MODE", "none")

from fastmcp.exceptions import ToolError  # noqa: E402
from fastmcp.server.auth.providers.github import GitHubProvider  # noqa: E402
from fastmcp.server.dependencies import get_access_token  # noqa: E402
from fastmcp.server.middleware import Middleware  # noqa: E402

from intervals_icu_mcp import server  # noqa: E402  (registriert alle Werkzeuge beim Import)

mcp = server.mcp
mcp.auth = GitHubProvider(
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    base_url=BASE_URL,
    jwt_signing_key=JWT_SIGNING_KEY,
)


class AllowList(Middleware):
    async def on_message(self, context, call_next):
        token = get_access_token()
        login = str((token.claims or {}).get("login", "")).lower() if token else ""
        if not login or login not in ALLOWED:
            raise ToolError("Nicht angemeldet oder nicht freigegeben.")
        return await call_next(context)


mcp.add_middleware(AllowList())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    mcp.run(transport="http", host="0.0.0.0", port=port)
