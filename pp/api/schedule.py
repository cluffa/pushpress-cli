from __future__ import annotations

from pp.http import PPClient

_GET_CLASSES = """query GetClasses($classDate: Date!) {
  classes: getCalendarItems(getCalendarItemsInput: {startDate: $classDate, endDate: $classDate, calendarSessionTypeId: 2}) {
    uuid
    title
    attendanceCap
    classType: typeName
    spotsAvailable
    isAllDay
    registrationStartOffset
    registrationEndOffset
    startTime: startDatetime
    endTime: endDatetime
    location {
      name
      __typename
    }
    mainCoach {
      ...CoachProfile
      __typename
    }
    __typename
  }
  __typename
}

fragment CoachProfile on Profile {
  userUuid
  firstName
  lastName
  gender
  primaryImage
  __typename
}"""

_GET_CLASS = """query GetClass($classId: String!) {
  getClass: getCalendarItem(getCalendarItemInput: {uuid: $classId}) {
    uuid
    title
    price
    description
    attendanceCap
    spotsAvailable
    isAllDay
    registrationStartOffsetInMins: registrationStartOffset
    registrationEndOffsetInMins: registrationEndOffset
    registrationLateCancelOffset
    rawStartTime: startDatetime
    rawEndTime: endDatetime
    location {
      name
      link
      __typename
    }
    mainCoach {
      ...CoachProfile
      __typename
    }
    assistantCoach {
      ...CoachProfile
      __typename
    }
    registrations: attendees {
      name: customerName
      image: primaryImage
      registrationTimestamp
      waitlistPriority
      uuid
      status
      userUuid
      __typename
    }
    type: calendarItemType {
      uuid
      name
      __typename
    }
    __typename
  }
  __typename
}

fragment CoachProfile on Profile {
  userUuid
  firstName
  lastName
  gender
  primaryImage
  __typename
}"""


def classes(c: PPClient, date: str) -> dict:
    return c.post("/v2/graph/graphql", json={
        "query": _GET_CLASSES,
        "variables": {"classDate": date},
    })


def class_detail(c: PPClient, class_id: str) -> dict:
    return c.post("/v2/graph/graphql", json={
        "query": _GET_CLASS,
        "variables": {"classId": class_id},
    })
