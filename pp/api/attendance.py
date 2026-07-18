from __future__ import annotations

from pp.http import PPClient

_QUERY = """query GetAttendanceStats($userUuid: String!, $clientUuid: String!) {
  getAttendanceStats(getAttendanceStatsInput: {clientUuid: $clientUuid, userUuid: $userUuid}) {
    week month year allTime __typename
  }
  __typename
}"""


def get_attendance_stats(c: PPClient, client_uuid: str, user_uuid: str) -> dict:
    return c.post("/v2/graph/graphql", json={
        "query": _QUERY,
        "variables": {"clientUuid": client_uuid, "userUuid": user_uuid},
    })
