from __future__ import annotations

from pp.http import PPClient


def gym(c: PPClient, client_uuid: str) -> dict:
    data = c.get(f"/v2/client/client/{client_uuid}")
    if isinstance(data, dict):
        data.pop("_eventEmitter", None)
    return data


def features(c: PPClient, client_uuid: str) -> dict:
    return c.get(f"/v2/client/client/{client_uuid}/features")


def settings(c: PPClient, client_uuid: str, type: str, name: str | None = None) -> dict:
    params = {"type": type}
    if name is not None:
        params["name"] = name
    return c.get(f"/v2/client/client/{client_uuid}/setting", params=params)
