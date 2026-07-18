from __future__ import annotations

_CATALOG = [
    {"command": "attendance", "summary": "Class attendance stats (week, month, year, all-time).",
     "args": [], "endpoint": "POST /v2/graph/graphql (GetAttendanceStats)",
     "output": "getAttendanceStats{week,month,year,allTime}"},
    {"command": "appointments", "summary": "Appointments: upcoming reservations, types, packages, credits, or history.",
     "args": [{"name": "--types", "required": False}, {"name": "--packages", "required": False},
              {"name": "--credits", "required": False}, {"name": "--history", "required": False}],
     "endpoint": "POST /v2/graph/graphql (AppointmentTypes / AppointmentPackages / AppointmentCreditCounts / AppointmentHistory / GetUpcomingReservations)",
     "output": "getAppointmentTypes[{uuid,name,duration,...}] or getAppointmentPackages[{uuid,name,price,...}] or getUserAppointmentCreditsCount[{appointmentTypeUuid,count}] or getUserAppointmentHistory[{uuid,startTime,endTime,eventStatus,staff,type}] or getUpcomingReservations[{id,uuid,reservationTitle,startTime,endTime,calendarItem{...}}]"},

    {"command": "whoami", "summary": "Verify stored token and print payload.",
     "args": [], "endpoint": "GET /v2/auth/verify/{token}",
     "output": "isValid, payload{clientUuid,role,sub,exp,iat,permissions}"},
    {"command": "gym", "summary": "Gym/company configuration.",
     "args": [{"name": "--client-uuid", "required": False}],
     "endpoint": "GET /v2/client/client/{clientUuid}",
     "output": "id,uuid,company,email,timezone,gmtOffset,planType,logoUrl,..."},
    {"command": "features", "summary": "Feature-flag map.",
     "args": [{"name": "--client-uuid", "required": False}],
     "endpoint": "GET /v2/client/client/{clientUuid}/features",
     "output": "{<flagName>: bool}"},
    {"command": "settings", "summary": "Client settings of a type.",
     "args": [{"name": "type", "required": True}, {"name": "--name", "required": False}],
     "endpoint": "GET /v2/client/client/{clientUuid}/setting?type=..",
     "output": "page,limit,hasMore,total,data[{id,type,name,value,...}]"},
    {"command": "feed", "summary": "Gym social feed activity.",
     "args": [{"name": "--limit", "required": False}, {"name": "--offset", "required": False}],
     "endpoint": "GET /v2/social-feed/feedActivity?gymId=..",
     "output": "activities[{actor,verb,object,time,reaction_counts,...}],limit,offset"},
    {"command": "graphql", "summary": "Raw GraphQL query.",
     "args": [{"name": "-q/--query", "required": True}, {"name": "--vars", "required": False}],
     "endpoint": "POST /v2/graph/graphql", "output": "{data,errors}"},
    {"command": "profile", "summary": "User profile with memberships and subscriptions.",
     "args": [], "endpoint": "POST /v2/graph/graphql (GetProfiles)",
     "output": "firstName,lastName,email,phone,membershipStatus,subscriptions[{plan,usage}]"},
    {"command": "schedule", "summary": "Class schedule for a date, or detail for a single class.",
     "args": [{"name": "--date", "required": False}, {"name": "--class-id", "required": False}],
     "endpoint": "POST /v2/graph/graphql (GetClasses / GetClass)",
     "output": "classes[{uuid,title,classType,spotsAvailable,startTime,endTime,location,mainCoach}] or getClass[{uuid,title,price,description,registrations,type}]"},
    {"command": "raw", "summary": "Raw GET passthrough (read-only).",
     "args": [{"name": "method", "required": True}, {"name": "path", "required": True},
              {"name": "--query", "required": False}],
     "endpoint": "GET {path}", "output": "upstream JSON"},
    {"command": "scores", "summary": "Workout leaderboard or personal score history.",
     "args": [{"name": "--part-uid", "required": False}, {"name": "--date", "required": False},
              {"name": "--keyword", "required": False}, {"name": "--workout-uid", "required": False},
              {"name": "--class-type-id", "required": False}],
     "endpoint": "POST /v2/graph/graphql (GetWorkoutScores / UserScoreHistory)",
     "output": "workoutGetScores{scores[{id,primaryScore,...}]} or scoreHistory[{title,primaryScore,...}]"},
    {"command": "benchmarks", "summary": "Benchmark workouts: list categories, find workouts, view history.",
     "args": [{"name": "--type", "required": False}, {"name": "--search", "required": False},
              {"name": "--part-uid", "required": False}, {"name": "--workout-uid", "required": False}],
     "endpoint": "POST /v2/graph/graphql (BenchmarkTypes / GetBenchmarkWorkouts / GetBenchmarkWorkoutHistory / GetWeightliftingWorkoutHistory)",
     "output": "benchmarkTypes[{key,displayName}] or benchmarks[{workoutUid,title}] or benchmarkWorkoutHistory[{workout{...},bestResult{...},results[{...}]}] or weightliftingWorkoutHistory[{workout{...},workingMax{...},results[{...}]}]"},
    {"command": "events", "summary": "Events calendar.",
     "args": [{"name": "--start-date", "required": False}, {"name": "--end-date", "required": False}],
     "endpoint": "POST /v2/graph/graphql (GetEvents)",
     "output": "events[{uuid,title,price,isAllDay,startTime,endTime,registrations[{uuid,userUuid}]}]"},
    {"command": "preorders", "summary": "Merchandise / product preorders.",
     "args": [], "endpoint": "POST /v2/graph/graphql (GetPreorders)",
     "output": "preorders[{uuid,name,startTimestamp,endTimestamp,productImage,purchased}]"},
    {"command": "workouts", "summary": "Workout types, WOD, parts, and score history.",
     "args": [{"name": "--date", "required": False}, {"name": "--type-id", "required": False},
              {"name": "--part-id", "required": False}, {"name": "--workout-uid", "required": False},
              {"name": "--score-id", "required": False}, {"name": "--keyword", "required": False}],
     "endpoint": "POST /v2/graph/graphql (GetWorkoutTypes / GetWorkoutOfDay / GetWorkoutPart / GetWorkoutScores / UserScoreHistory)",
     "output": "workoutTypes[{name,uid,...}] or workoutOfDay{title,parts[{title,scoreType,...}]} or workoutPart{title,scoreType,...} or workoutGetScores{scores[{id,primaryScore,...}]} or scoreHistory[{title,primaryScore,...}]"},
]


def catalog() -> list:
    return [dict(c) for c in _CATALOG]


def for_command(name: str):
    for c in _CATALOG:
        if c["command"] == name:
            return dict(c)
    return None
