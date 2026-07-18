from __future__ import annotations

from pp.http import PPClient
from pp.api.workouts import _SHARED_FRAGMENTS

_BENCHMARK_TYPES = """
query BenchmarkTypes {
  benchmarkTypes: benchmarkTypes {
    key
    displayName
    __typename
  }
  __typename
}"""

_GET_BENCHMARK_WORKOUTS = """
query GetBenchmarkWorkouts($benchmarkType: String, $searchString: String) {
  benchmarks: benchmarkWorkouts(benchmarkWorkoutsInput: {benchmarkType: $benchmarkType, searchString: $searchString}) {
    workoutUid
    title
    workoutTitle
    __typename
  }
  __typename
}"""

_GET_BENCHMARK_WORKOUT_HISTORY = _SHARED_FRAGMENTS + """
query GetBenchmarkWorkoutHistory($workoutPartUid: String!) {
  benchmarkWorkoutHistory(benchmarkWorkoutHistoryInput: {workoutPartUid: $workoutPartUid}) {
    workout {
      ...WorkoutOfDayPart
      __typename
    }
    bestResult {
      ...WorkoutScore
      __typename
    }
    results {
      ...WorkoutScore
      __typename
    }
    __typename
  }
  __typename
}"""

_GET_WEIGHTLIFTING_WORKOUT_HISTORY = _SHARED_FRAGMENTS + """
query GetWeightliftingWorkoutHistory($workoutUid: String!) {
  weightliftingWorkoutHistory(weightliftingWorkoutHistoryInput: {workoutUid: $workoutUid}) {
    workout {
      ...WorkoutOfDayPart
      __typename
    }
    workingMax {
      ...WorkoutScore
      __typename
    }
    results {
      ...WorkoutScore
      __typename
    }
    __typename
  }
  __typename
}"""


def benchmark_types(c: PPClient) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _BENCHMARK_TYPES, "variables": {}})


def benchmark_workouts(c: PPClient, benchmark_type: str | None = None, search: str | None = None) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _GET_BENCHMARK_WORKOUTS, "variables": {"benchmarkType": benchmark_type, "searchString": search}})


def benchmark_history(c: PPClient, workout_part_uid: str) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _GET_BENCHMARK_WORKOUT_HISTORY, "variables": {"workoutPartUid": workout_part_uid}})


def weightlifting_history(c: PPClient, workout_uid: str) -> dict:
    return c.post("/v2/graph/graphql", json={"query": _GET_WEIGHTLIFTING_WORKOUT_HISTORY, "variables": {"workoutUid": workout_uid}})
