from __future__ import annotations

from pp.http import PPClient

# Individual fragments — used only as needed per query
_F_WORKOUT_OF_DAY_PART = """
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
"""

_F_WORKOUT_OF_DAY = """
fragment WorkoutOfDay on WorkoutOfDay {
  uid id origin createdDate publishedOn rawPublishingDate: publishingDate
  tenantId title updatedDate version workoutUid classTypeId notified
  workoutState imageUrl imageUrlId videoUrlId workoutProgramGroupId day
  workoutProgramTemplateId publishingTime
  parts { ...WorkoutOfDayPart __typename }
  __typename
}
"""

_F_WORKOUT_SCORE = """
fragment WorkoutScore on WorkoutLogScore {
  id division rawDate: date classTypeId athleteDisplayName athleteImageUri
  rawUnit: unit primaryScore secondaryScore athleteComment mine
  likes { ...WorkoutLike __typename }
  comments { ...WorkoutComment __typename }
  sets { ...WorkoutSet __typename }
  __typename
}
"""

_F_WORKOUT_MEDIA = """
fragment WorkoutMedia on WorkoutOfDayMedia { id title mediaUrl __typename }
"""

_F_WORKOUT_LIKE = """
fragment WorkoutLike on LogScoreLikes {
  id rawCreatedTime: createdTime mine
  athlete { ...WorkoutAthlete __typename }
  __typename
}
"""

_F_WORKOUT_ATHLETE = """
fragment WorkoutAthlete on LogScoreAthlete {
  athleteUid firstName lastName id profilePicture __typename
}
"""

_F_WORKOUT_COMMENT = """
fragment WorkoutComment on WorkoutComment {
  id comment entityId entityType rawDate: date status media mediaType resourceId mine
  athlete { ...WorkoutAthlete __typename }
  likes { ...WorkoutLike __typename }
  __typename
}
"""

_F_WORKOUT_SET = """
fragment WorkoutSet on LogScoreSets { primaryScore secondaryScore __typename }
"""

# Fragment groups for each query — only includes fragments transitively used
_FOR_WORKOUT_OF_DAY = (
    _F_WORKOUT_OF_DAY
    + _F_WORKOUT_OF_DAY_PART
    + _F_WORKOUT_MEDIA
    + _F_WORKOUT_SCORE
    + _F_WORKOUT_LIKE
    + _F_WORKOUT_ATHLETE
    + _F_WORKOUT_COMMENT
    + _F_WORKOUT_SET
)

_FOR_WORKOUT_PART = _FOR_WORKOUT_OF_DAY  # Same transitive closure

_FOR_WORKOUT_SCORES = (
    _F_WORKOUT_SCORE
    + _F_WORKOUT_LIKE
    + _F_WORKOUT_ATHLETE
    + _F_WORKOUT_COMMENT
    + _F_WORKOUT_SET
)

# Public: shared fragment block for use by other modules (e.g. benchmarks.py)
# Includes the full transitive closure for WorkoutOfDayPart + WorkoutScore.
WORKOUT_SHARED_FRAGMENTS = _FOR_WORKOUT_OF_DAY

_GET_WORKOUT_TYPES = """
query GetWorkoutTypes($classDate: String!) {
  workoutTypes: getClassTypes(getClassTypesInput: {date: $classDate}) {
    name origin uid static progressiveProgram lastDayNum __typename
  }
  __typename
}
"""

_GET_WORKOUT_OF_DAY = _FOR_WORKOUT_OF_DAY + """
query GetWorkoutOfDay($classDate: String!, $classTypeId: String!) {
  workoutOfDay: getWorkoutOfDay(getWorkoutOfDayInput: {date: $classDate, classTypeUid: $classTypeId}) {
    ...WorkoutOfDay __typename
  }
  __typename
}
"""

_GET_WORKOUT_PART = _FOR_WORKOUT_PART + """
query GetWorkoutPart($workoutPartId: String!, $workoutUid: String, $scoreId: Int) {
  workoutPart: getWorkoutPart(getWorkoutPartInput: {workoutPartUid: $workoutPartId, workoutUid: $workoutUid, scoreId: $scoreId}) {
    ...WorkoutOfDayPart __typename
  }
  __typename
}
"""

_GET_WORKOUT_SCORES = _FOR_WORKOUT_SCORES + """
query GetWorkoutScores($workoutUid: String, $classTypeId: Float, $workoutPartUid: String!, $date: String!) {
  workoutGetScores(workoutGetScoresInput: {classTypeId: $classTypeId, date: $date, workoutPartUid: $workoutPartUid, workoutUid: $workoutUid}) {
    scores { ...WorkoutScore __typename } __typename
  }
  __typename
}
"""

_USER_SCORE_HISTORY = """
query UserScoreHistory($keyword: String!) {
  scoreHistory: userScoreHistory(userScoreHistoryInput: {keyword: $keyword}) {
    workoutUid workoutScoreId primaryScore secondaryScore
    workoutDateRaw: workoutDate workoutTitle workoutPartUid title scoreType measurementUnit __typename
  }
  __typename
}
"""


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


def wod_auto(c: PPClient, date: str) -> dict:
    """Auto-discover the class type and return today's WOD.

    Calls getClassTypes to find available class types, then fetches the
    WOD for the first one that has a workout. Returns a dict with keys:
    date, class_type_name, class_type_uid, workout (the WOD payload or None).
    """
    types_resp = workout_types(c, date)
    types = types_resp.get("data", {}).get("workoutTypes", [])

    for ct in types:
        ct_uid = ct.get("uid")
        ct_name = ct.get("name", "Unknown")
        if not ct_uid:
            continue
        wod_resp = workout_of_day(c, date, ct_uid)
        wod_data = wod_resp.get("data", {}).get("workoutOfDay", [])
        if wod_data:
            # workoutOfDay may be a list or a single object
            if isinstance(wod_data, list):
                wod = wod_data[0] if wod_data else None
            else:
                wod = wod_data
            if wod:
                return {
                    "date": date,
                    "class_type_name": ct_name,
                    "class_type_uid": ct_uid,
                    "workout": wod,
                }

    return {
        "date": date,
        "class_type_name": "",
        "class_type_uid": "",
        "workout": None,
    }
