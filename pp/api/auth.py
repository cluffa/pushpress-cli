from __future__ import annotations

from pp.http import PPClient
from pp.models import Session


def login(email: str, password: str, base_url: str | None = None) -> Session:
    client = PPClient(token="", base_url=base_url)
    # The login endpoint expects the account email under "username".
    data = client.post("/v2/auth/login", json={"username": email, "password": password})
    return Session.from_access_data(data)


def verify(client: PPClient, token: str) -> dict:
    return client.get(f"/v2/auth/verify/{token}")
