from __future__ import annotations

from datetime import datetime, timezone

from pp.errors import PPError
from pp.http import PPClient
from pp.models import Session


def login(email: str, password: str, base_url: str | None = None) -> Session:
    client = PPClient(token="", base_url=base_url)
    # The login endpoint expects the account email under "username".
    data = client.post("/v2/auth/login", json={"username": email, "password": password})
    return Session.from_access_data(_normalize_login_data(client, data))


def verify(client: PPClient, token: str) -> dict:
    return client.get(f"/v2/auth/verify/{token}")


def _normalize_login_data(client: PPClient, data) -> dict:
    """Flatten a login response into the access-data shape Session expects.

    The live response carries identity per gym under "clients" (a list) and
    only the token at the top level, so reading clientUuid/userUuid off the
    top level yields empty strings. Pick the client entry the issued token
    belongs to and merge its identity fields up. Flat responses (no
    "clients" key) pass through unchanged.
    """
    if not isinstance(data, dict):
        return {}
    clients = data.get("clients")
    if not isinstance(clients, list) or not clients:
        return data
    token = data.get("accessToken", "")
    payload = _verify_payload(client, token)
    entry = _select_client(clients, token, payload)
    merged = dict(entry)
    merged["accessToken"] = token or entry.get("accessToken", "")
    if payload:
        # The token payload is authoritative for identity and expiry.
        if payload.get("clientUuid"):
            merged["clientUuid"] = payload["clientUuid"]
        user_uuid = payload.get("userUuid") or payload.get("sub")
        if user_uuid:
            merged["userUuid"] = user_uuid
        exp = payload.get("exp")
        if exp:
            merged["tokenExpiration"] = datetime.fromtimestamp(exp, tz=timezone.utc).isoformat()
    return merged


def _verify_payload(client: PPClient, token: str) -> dict:
    """Best-effort token introspection; {} when verify is unavailable."""
    if not token:
        return {}
    try:
        result = verify(PPClient(token=token, base_url=client.base_url), token)
    except PPError:
        return {}
    if isinstance(result, dict):
        payload = result.get("payload")
        if isinstance(payload, dict):
            return payload
    return {}


def _select_client(clients: list, token: str, payload: dict) -> dict:
    """Choose the clients[] entry the issued token belongs to."""
    entries = [e for e in clients if isinstance(e, dict)]
    client_uuid = payload.get("clientUuid")
    if client_uuid:
        for entry in entries:
            if entry.get("clientUuid") == client_uuid:
                return entry
    if token:
        for entry in entries:
            if entry.get("accessToken") == token:
                return entry
    for entry in entries:
        if entry.get("active"):
            return entry
    return entries[0] if entries else {}
