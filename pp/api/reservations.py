from __future__ import annotations

from pp.api import profile as profileapi
from pp.errors import UpstreamError, UsageError
from pp.http import PPClient

# Mutation documents recovered from the members.pushpress.com web build
# (main.dart.js) and verified live. Each root field takes a single
# `…Input` object argument, per the API convention in docs/API.md.
# `source` is a nullable String the app may omit; null is accepted.

_CREATE_RESERVATION = """mutation CreateReservation($clientUserUuid: String!, $calendarItemUuid: String!, $subscriptionUuid: String!, $source: String) {
  createReservation(createReservationInput: {clientUserUuid: $clientUserUuid, calendarItemUuid: $calendarItemUuid, subscriptionUuid: $subscriptionUuid, source: $source}) {
    uuid
    __typename
  }
  __typename
}"""

_CANCEL_RESERVATION = """mutation CancelReservation($reservationId: String!) {
  cancelReservation(cancelReservationInput: {reservationId: $reservationId}) {
    uuid
    __typename
  }
  __typename
}"""

_CHECKIN = """mutation CheckIn($reservationId: String!, $source: String) {
  checkin(checkinInput: {reservationId: $reservationId, source: $source}) {
    uuid
    __typename
  }
  __typename
}"""


def _checked(result: dict) -> dict:
    """Raise a clean error when the API answers 200 with GraphQL errors."""
    errors = result.get("errors") if isinstance(result, dict) else None
    if errors:
        first = errors[0]
        message = first.get("message", "graphql error") if isinstance(first, dict) else str(first)
        raise UpstreamError("api rejected the request", detail=message)
    return result


def _mutate(c: PPClient, query: str, variables: dict) -> dict:
    return _checked(c.post("/v2/graph/graphql", json={"query": query, "variables": variables}))


def booking_identity(c: PPClient, client_uuid: str, user_uuid: str) -> tuple[str, str]:
    """Resolve (clientUserUuid, subscriptionUuid) for createReservation.

    Both values come from the member's own profile: the client-user UUID
    and the first active subscription (falling back to the first listed).
    """
    result = profileapi.get_profile(c, client_uuid, user_uuid)
    profile = (result.get("data") or {}).get("profile") or {}
    client_user_uuid = profile.get("clientUserUuid")
    if not client_user_uuid:
        raise UpstreamError("could not resolve client user uuid", detail="profile returned no clientUserUuid")
    subscriptions = profile.get("subscriptions") or []
    active = next((s for s in subscriptions if s.get("active")), None)
    chosen = active or (subscriptions[0] if subscriptions else None)
    subscription_uuid = (chosen or {}).get("subscriptionUuid")
    if not subscription_uuid:
        raise UsageError(
            "no subscription on profile",
            hint="an active membership subscription is required to reserve a class",
        )
    return client_user_uuid, subscription_uuid


def create_reservation(
    c: PPClient,
    client_user_uuid: str,
    calendar_item_uuid: str,
    subscription_uuid: str,
    source: str | None = None,
) -> dict:
    return _mutate(c, _CREATE_RESERVATION, {
        "clientUserUuid": client_user_uuid,
        "calendarItemUuid": calendar_item_uuid,
        "subscriptionUuid": subscription_uuid,
        "source": source,
    })


def cancel_reservation(c: PPClient, reservation_id: str) -> dict:
    return _mutate(c, _CANCEL_RESERVATION, {"reservationId": reservation_id})


def checkin_reservation(c: PPClient, reservation_id: str, source: str | None = None) -> dict:
    return _mutate(c, _CHECKIN, {"reservationId": reservation_id, "source": source})
