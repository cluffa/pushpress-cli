from __future__ import annotations
from pp.http import PPClient

_QUERY = """query GetPreorders($userUuid: String) {
  preorders: getPreorders(getPreordersInput: {userUuid: $userUuid}) {
    uuid name startTimestamp endTimestamp productImage purchased __typename
  }
  __typename
}"""


def get_preorders(c: PPClient, user_uuid: str | None = None) -> dict:
    return c.post("/v2/graph/graphql", json={
        "query": _QUERY,
        "variables": {"userUuid": user_uuid},
    })
