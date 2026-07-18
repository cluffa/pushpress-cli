from __future__ import annotations

from pp.http import PPClient

# Shared fragments used across multiple workout queries
_SHARED_FRAGMENTS = """
fragment WorkoutOfDayPart on WorkoutOfDayParts {
  workoutPartUid
  description
  scoreType
  title
  workoutTitle
  athletesNotes
  coachesNotes
  scoreCount
  sets
  divisions
  defaultReps
  rawUnit: unit
  media { ...WorkoutMedia __typename }
  score { ...WorkoutScore __typename }
  __typename
}

fragment WorkoutOfDay on WorkoutOfDay {
  uid id origin createdDate publishedOn rawPublishingDate: publishingDate
  tenantId title updatedDate version workoutUid classTypeId notified
  workoutState imageUrl imageUrlId videoUrlId workoutProgramGroupId day
  workoutProgramTemplateId publishingTime
  parts { ...WorkoutOfDayPart __typename }
  __typename
}

fragment WorkoutScore on WorkoutLogScore {
  id division rawDate: date classTypeId athleteDisplayName athleteImageUri
  rawUnit: unit primaryScore secondaryScore athleteComment mine
  likes { ...WorkoutLike __typename }
  comments { ...WorkoutComment __typename }
  sets { ...WorkoutSet __typename }
  __typename
}

fragment WorkoutMedia on WorkoutOfDayMedia { id title mediaUrl __typename }

fragment WorkoutLike on LogScoreLikes {
  id rawCreatedTime: createdTime mine
  athlete { ...WorkoutAthlete __typename }
  __typename
}

fragment WorkoutAthlete on LogScoreAthlete {
  athleteUid firstName lastName id profilePicture __typename
}

fragment WorkoutComment on WorkoutComment {
  id comment entityId entityType rawDate: date status media mediaType resourceId mine
  athlete { ...WorkoutAthlete __typename }
  likes { ...WorkoutLike __typename }
  __typename
}

fragment WorkoutSet on LogScoreSets { primaryScore secondaryScore __typename }
"""

_GET_WORKOUT_TYPES = _SHARED_FRAGMENTS + """
query GetWorkoutTypes($classDate: String!) {
  workoutTypes: getClassTypes(getClassTypesInput: {date: $classDate}) {
    name origin uid static progressiveProgram lastDayNum __typename
  }
  __typename
}"""

_GET_WORKOUT_OF_DAY = _SHARED_FRAGMENTS + """
query GetWorkoutOfDay($classDate: String!, $classTypeId: String!) {
  workoutOfDay: getWorkoutOfDay(getWorkoutOfDayInput: {date: $classDate, classTypeUid: $classTypeId}) {
    ...WorkoutOfDay __typename
  }
  __typename
}"""

_GET_WORKOUT_PART = _SHARED_FRAGMENTS + """
query GetWorkoutPart($workoutPartId: String!, $workoutUid: String, $scoreId: Int) {
  workoutPart: getWorkoutPart(getWorkoutPartInput: {workoutPartUid: $workoutPartId, workoutUid: $workoutUid, scoreId: $scoreId}) {
    ...WorkoutOfDayPart __typename
  }
  __typename
}"""

_GET_WORKOUT_SCORES = _SHARED_FRAGMENTS + """
query GetWorkoutScores($workoutUid: String, $classTypeId: Float, $workoutPartUid: String!, $date: String!) {
  workoutGetScores(workoutGetScoresInput: {classTypeId: $classTypeId, date: $date, workoutPartUid: $workoutPartUid, workoutUid: $workoutUid}) {
    scores { ...WorkoutScore __typename } __typename
  }
  __typename
}"""

_USER_SCORE_HISTORY = """
query UserScoreHistory($keyword: String!) {
  scoreHistory: userScoreHistory(userScoreHistoryInput: {keyword: $keyword}) {
    workoutUid workoutScoreId primaryScore secondaryScore
    workoutDateRaw: workoutDate workoutTitle workoutPartUid title scoreType measurementUnit __typename
  }
  __typename
}"""


def workout_types(c: PPClient, date: str) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _GET_WORKOUT_TYPES, "variables": {"classDate": date}})


def workout_of_day(c: PPClient, date: str, class_type_id: str) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _GET_WORKOUT_OF_DAY, "variables": {"classDate": date, "classTypeId": class_type_id}})


def workout_part(c: PPClient, part_id: str, workout_uid: str | None = None, score_id: int | None = None) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _GET_WORKOUT_PART, "variables": {"workoutPartId": part_id, "workoutUid": workout_uid, "scoreId": score_id}})


def workout_scores(c: PPClient, part_uid: str, date: str, workout_uid: str | None = None, class_type_id: float | None = None) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _GET_WORKOUT_SCORES, "variables": {"workoutPartUid": part_uid, "date": date, "workoutUid": workout_uid, "classTypeId": class_type_id}})


def score_history(c: PPClient, keyword: str) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _USER_SCORE_HISTORY, "variables": {"keyword": keyword}})
