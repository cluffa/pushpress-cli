from __future__ import annotations

from pp.http import PPClient

_QUERY = """query GetProfiles($clientUuid: String!, $userUuid: String!) {
  profile: getProfile(getProfileInput: {clientUuid: $clientUuid, userUuid: $userUuid}) {
    ...ProfileFragment
    linkedAccounts {
      ...ProfileFragment
      __typename
    }
    __typename
  }
  __typename
}

fragment ProfileFragment on Profile {
  clientUserUuid
  email
  username
  clientUuid
  userUuid
  parentUserId
  firstName
  lastName
  birthday
  gender
  phone
  address1
  address2
  city
  state
  postalCode
  country
  emergencyName
  emergencyPhone
  emergencyRelationship
  primaryImage
  activateTimestamp
  membershipStatus {
    code
    __typename
  }
  subscriptions {
    subscriptionUuid
    status
    active
    startDate
    endDate
    totalOccurrences
    plan
    currentPeriodUsage {
      limit
      period
      periodStart
      periodEnd
      checkins
      reservations
      lateCancels
      waitlists
      noShows
      available
      __typename
    }
    planObject {
      uuid
      name
      allowCheckins
      acceptedTypeUuids: planCalendarItemTypes {
        uuid: calenderItemTypeUuid
        __typename
      }
      type
      interval
      intervalType
      __typename
    }
    __typename
  }
  __typename
}"""


def get_profile(c: PPClient, client_uuid: str, user_uuid: str) -> dict:
    return c.post("/v2/graph/graphql", json={
        "query": _QUERY,
        "variables": {"clientUuid": client_uuid, "userUuid": user_uuid},
    })
