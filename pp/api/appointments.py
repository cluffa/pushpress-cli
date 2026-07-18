from __future__ import annotations

from pp.http import PPClient

_APPOINTMENT_TYPE_FRAGMENT = """
fragment AppointmentTypeFragment on AppointmentType {
  uuid
  name
  duration
  lateCancel
  availability {
    dayOfTheWeek
    __typename
  }
  __typename
}"""

_APPOINTMENT_TYPE_STAFF_FRAGMENT = """
fragment AppointmentTypeStaffFragment on User {
  uuid
  firstName
  lastName
  primaryImage
  __typename
}"""

_APPOINTMENT_TYPES = """query AppointmentTypes {
  types: getAppointmentTypes {
    ...AppointmentTypeFragment
    __typename
  }
  __typename
}
""" + _APPOINTMENT_TYPE_FRAGMENT

_APPOINTMENT_PACKAGES = """query AppointmentPackages {
  packages: getAppointmentPackages {
    uuid
    name
    description
    longDescription
    hasTax
    availableOnMemberApp
    rawTaxRatePercentage: taxPrice
    discount {
      type: discountType
      value: discountValue
      __typename
    }
    isFree
    packagePrice
    numberOfSessions
    appointmentType {
      uuid
      name
      __typename
    }
    __typename
  }
  __typename
}"""

_APPOINTMENT_CREDIT_COUNTS = """query AppointmentCreditCounts($userUuid: ID!) {
  counts: getUserAppointmentCreditsCount(input: {userUuid: $userUuid}) {
    appointmentTypeUuid
    count
    __typename
  }
  __typename
}"""

_APPOINTMENT_HISTORY = """query AppointmentHistory($userUuid: String!) {
  history: getUserAppointmentHistory(getUserAppointmentHistoryInput: {userUuid: $userUuid}) {
    uuid
    rawStartTime: startTime
    rawEndTime: endTime
    eventStatus
    staff {
      ...AppointmentTypeStaffFragment
      __typename
    }
    type: appointmentType {
      ...AppointmentTypeFragment
      __typename
    }
    __typename
  }
  __typename
}
""" + _APPOINTMENT_TYPE_STAFF_FRAGMENT + _APPOINTMENT_TYPE_FRAGMENT

_UPCOMING_RESERVATIONS = """query GetUpcomingReservations {
  reservations: getUpcomingReservations {
    id
    uuid
    reservationTitle
    calendarItemId
    calendarItemUuid
    isActive
    isCancelled
    user
    subscription
    clientUuid
    userId
    clientId
    lateCancel
    waitlisted
    waitlistUntilTimestamp
    registrationTimestamp
    orderId
    clientUserUuid
    rawStartTime: reservationStart
    rawEndTime: reservationEnd
    rawStatus: status
    calendarItem {
      calendarItemType {
        name
        __typename
      }
      location {
        name
        link
        __typename
      }
      mainCoach {
        firstName
        lastName
        primaryImage
        __typename
      }
      assistantCoach {
        firstName
        lastName
        primaryImage
        __typename
      }
      __typename
    }
    __typename
  }
  __typename
}"""


def appointment_types(c: PPClient) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _APPOINTMENT_TYPES, "variables": {}})


def appointment_packages(c: PPClient) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _APPOINTMENT_PACKAGES, "variables": {}})


def appointment_credit_counts(c: PPClient, user_uuid: str) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _APPOINTMENT_CREDIT_COUNTS, "variables": {"userUuid": user_uuid}})


def appointment_history(c: PPClient, user_uuid: str) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _APPOINTMENT_HISTORY, "variables": {"userUuid": user_uuid}})


def upcoming_reservations(c: PPClient) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _UPCOMING_RESERVATIONS, "variables": {}})
