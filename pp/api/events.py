from __future__ import annotations
from pp.http import PPClient

_QUERY = """query GetEvents($startDate: Date!, $endDate: Date!) {
  events: getCalendarItems(getCalendarItemsInput: {startDate: $startDate, endDate: $endDate, calendarSessionTypeId: 1}) {
    uuid title price isAllDay startTime: startDatetime endTime: endDatetime
    registrations { uuid userUuid __typename } __typename
  }
  __typename
}"""


def get_events(c: PPClient, start_date: str, end_date: str) -> dict:
    return c.post("/v2/graph/graphql", json={
        "query": _QUERY,
        "variables": {"startDate": start_date, "endDate": end_date},
    })
