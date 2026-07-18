from __future__ import annotations

from pp.http import PPClient


def query(c: PPClient, query: str, variables: dict | None = None) -> dict:
    return c.post("/v2/graph/graphql", json={"query": query, "variables": variables or {}})
