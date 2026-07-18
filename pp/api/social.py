from __future__ import annotations

from pp.http import PPClient


def feed(c: PPClient, gym_id: str, limit: int = 20, offset: int = 0) -> dict:
    return c.get(
        "/v2/social-feed/feedActivity",
        params={"gymId": gym_id, "limit": limit, "offset": offset},
    )
