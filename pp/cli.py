from __future__ import annotations

import json as _json
from dataclasses import dataclass
from datetime import datetime, timezone

import typer

from pp import __version__, session
from pp import describe as describemod
from pp.api import auth
from pp.api import appointments as apptapi
from pp.api import attendance as attendanceapi
from pp.api import benchmarks as benchmarkapi
from pp.api import client as clientapi
from pp.api import events as eventsapi
from pp.api import graphql as gqlapi
from pp.api import preorders as preorderapi
from pp.api import profile as profileapi
from pp.api import raw as rawapi
from pp.api import schedule as scheduleapi
from pp.api import scores as scoreapi
from pp.api import social as socialapi
from pp.api import workouts as workoutapi
from pp.errors import AuthError, NotFoundError, UsageError
from pp.http import PPClient, from_session
from pp.output import command, emit


@dataclass
class OutputOpts:
    human: bool = False
    ndjson: bool = False
    fields: list | None = None


app = typer.Typer(no_args_is_help=True, add_completion=False)


def _version_cb(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", callback=_version_cb, is_eager=True, help="Print version and exit."
    ),
    human: bool = typer.Option(False, "--human", help="Human-readable output instead of JSON."),
    ndjson: bool = typer.Option(False, "--ndjson", help="Stream lists as newline-delimited JSON."),
    fields: str = typer.Option(None, "--fields", help="Comma-separated fields to keep."),
):
    """pp — agent-first CLI for the PushPress Members API."""
    ctx.obj = OutputOpts(
        human=human,
        ndjson=ndjson,
        fields=[f.strip() for f in fields.split(",")] if fields else None,
    )


def _emit(ctx: typer.Context, data, human_renderer=None):
    o: OutputOpts = ctx.obj
    emit(data, human=o.human, ndjson=o.ndjson, fields=o.fields, human_renderer=human_renderer)


@app.command()
@command
def login(
    ctx: typer.Context,
    email: str = typer.Option(None, "--email", help="Account email."),
    password_stdin: bool = typer.Option(False, "--password-stdin", help="Read password from stdin."),
    token: str = typer.Option(None, "--token", help="Store a pre-obtained bearer token instead of logging in."),
):
    """Authenticate and store a session token."""
    if token:
        from pp.models import Session

        result = auth.verify(PPClient(token=token), token)
        payload = result.get("payload", {}) if isinstance(result, dict) else {}
        exp = payload.get("exp")
        if exp:
            token_expiration = datetime.fromtimestamp(exp, tz=timezone.utc).isoformat()
        else:
            token_expiration = ""
        sess = Session.from_access_data(
            {
                "accessToken": token,
                "tokenExpiration": token_expiration,
                "clientUuid": payload.get("clientUuid", ""),
                "userUuid": payload.get("sub", ""),
            }
        )
        # company / subdomain are not in the verify payload; they stay ""
        # and can be filled later by calling gym / whoami.
        session.save(sess)
        _emit(ctx, {"stored": True, "source": "token"})
        return
    if not email:
        raise UsageError("--email is required unless --token is given", hint="pp login --email you@example.com")
    if password_stdin:
        password = typer.get_text_stream("stdin").readline().rstrip("\n")
    else:
        password = typer.prompt("Password", hide_input=True)
    sess = auth.login(email, password)
    session.save(sess)
    _emit(ctx, {k: v for k, v in sess.to_dict().items() if k != "accessToken"})


@app.command()
@command
def whoami(ctx: typer.Context):
    """Verify the stored token and print its payload."""
    token = session.current_token()
    _emit(ctx, auth.verify(PPClient(token=token), token))


@app.command()
@command
def logout(ctx: typer.Context):
    """Delete the stored session."""
    session.clear()
    _emit(ctx, {"loggedOut": True})


@app.command()
@command
def profile(ctx: typer.Context):
    """User profile with memberships and subscriptions."""
    c = from_session()
    client_uuid = _client_uuid(None)
    user_uuid = session.load().user_uuid
    _emit(ctx, profileapi.get_profile(c, client_uuid, user_uuid))


@app.command()
@command
def schedule(
    ctx: typer.Context,
    date: str = typer.Option(None, "--date", help="Date YYYY-MM-DD (default today)."),
    class_id: str = typer.Option(None, "--class-id", help="Get detail for one class."),
):
    """Class schedule for a date, or detail for a single class."""
    c = from_session()
    if class_id:
        _emit(ctx, scheduleapi.class_detail(c, class_id))
    else:
        from datetime import date as dt
        d = date or dt.today().isoformat()
        _emit(ctx, scheduleapi.classes(c, d))


@app.command()
@command
def workouts(
    ctx: typer.Context,
    date: str = typer.Option(None, "--date", help="Date YYYY-MM-DD (default today)."),
    type_id: str = typer.Option(None, "--type-id", help="Class type UUID for WOD detail."),
    part_id: str = typer.Option(None, "--part-id", help="Workout part UUID for detail + your score."),
    workout_uid: str = typer.Option(None, "--workout-uid", help="Workout UUID for score context."),
    score_id: int = typer.Option(None, "--score-id", help="Score ID for workout part detail."),
    keyword: str = typer.Option(None, "--keyword", help="Search your score history."),
):
    """Workouts: list types, get WOD, drill into parts, or search score history."""
    c = from_session()
    from datetime import date as dt
    d = date or dt.today().isoformat()

    if keyword is not None:
        _emit(ctx, workoutapi.score_history(c, keyword))
    elif part_id:
        _emit(ctx, workoutapi.workout_part(c, part_id, workout_uid=workout_uid, score_id=score_id))
    elif type_id:
        _emit(ctx, workoutapi.workout_of_day(c, d, type_id))
    else:
        _emit(ctx, workoutapi.workout_types(c, d))


@app.command()
@command
def scores(
    ctx: typer.Context,
    part_uid: str = typer.Option(None, "--part-uid", help="Workout part UUID for leaderboard."),
    date: str = typer.Option(None, "--date", help="Date YYYY-MM-DD."),
    keyword: str = typer.Option(None, "--keyword", help="Search your score history."),
    workout_uid: str = typer.Option(None, "--workout-uid"),
    class_type_id: float = typer.Option(None, "--class-type-id"),
):
    """Workout leaderboard or personal score history."""
    c = from_session()
    if keyword is not None:
        _emit(ctx, scoreapi.history(c, keyword))
    elif part_uid and date:
        _emit(ctx, scoreapi.leaderboard(c, part_uid, date, workout_uid=workout_uid, class_type_id=class_type_id))
    else:
        raise UsageError("use --keyword for history, or --part-uid + --date for leaderboard")


@app.command()
@command
def benchmarks(
    ctx: typer.Context,
    type: str = typer.Option(None, "--type", help="Benchmark category (e.g. WEIGHTLIFTING, ENDURANCE)."),
    search: str = typer.Option(None, "--search", help="Search benchmark workouts by name."),
    part_uid: str = typer.Option(None, "--part-uid", help="Benchmark part UUID for history + best result."),
    workout_uid: str = typer.Option(None, "--workout-uid", help="Workout UUID for weightlifting history."),
):
    """Benchmark workouts: list categories, find workouts, view history."""
    c = from_session()
    if part_uid:
        _emit(ctx, benchmarkapi.benchmark_history(c, part_uid))
    elif workout_uid:
        _emit(ctx, benchmarkapi.weightlifting_history(c, workout_uid))
    elif type or search:
        _emit(ctx, benchmarkapi.benchmark_workouts(c, benchmark_type=type, search=search))
    else:
        _emit(ctx, benchmarkapi.benchmark_types(c))


def _client_uuid(override: str | None) -> str:
    if override:
        return override
    # Try session file first; fall back to resolving from token.
    try:
        uuid = session.load().client_uuid
        if uuid:
            return uuid
    except AuthError:
        pass
    token = session.current_token()
    result = auth.verify(PPClient(token=token), token)
    payload = result.get("payload", {}) if isinstance(result, dict) else {}
    uuid = payload.get("clientUuid", "")
    if not uuid:
        raise AuthError("could not resolve client UUID", hint="run: pp login")
    return uuid


@app.command()
@command
def gym(ctx: typer.Context, client_uuid: str = typer.Option(None, "--client-uuid")):
    """Gym / company configuration."""
    _emit(ctx, clientapi.gym(from_session(), _client_uuid(client_uuid)))


@app.command()
@command
def features(ctx: typer.Context, client_uuid: str = typer.Option(None, "--client-uuid")):
    """Feature-flag map for the gym."""
    _emit(ctx, clientapi.features(from_session(), _client_uuid(client_uuid)))


@app.command()
@command
def settings(
    ctx: typer.Context,
    type: str = typer.Argument(..., help="Setting type, e.g. core, train, pushpress-membersportal."),
    name: str = typer.Option(None, "--name", help="Single setting name to filter."),
    client_uuid: str = typer.Option(None, "--client-uuid"),
):
    """Client settings of a given type."""
    _emit(ctx, clientapi.settings(from_session(), _client_uuid(client_uuid), type=type, name=name))


@app.command()
@command
def feed(
    ctx: typer.Context,
    limit: int = typer.Option(20, "--limit"),
    offset: int = typer.Option(0, "--offset"),
    client_uuid: str = typer.Option(None, "--client-uuid"),
):
    """Gym social feed activity."""
    _emit(ctx, socialapi.feed(from_session(), _client_uuid(client_uuid), limit=limit, offset=offset))


@app.command()
@command
def graphql(
    ctx: typer.Context,
    query: str = typer.Option(..., "-q", "--query", help="GraphQL query document."),
    vars: str = typer.Option(None, "--vars", help="JSON string of variables."),
):
    """Send a raw GraphQL query to /v2/graph/graphql."""
    if vars:
        try:
            variables = _json.loads(vars)
        except ValueError as e:
            raise UsageError("invalid --vars JSON", detail=str(e))
    else:
        variables = None
    _emit(ctx, gqlapi.query(from_session(), query, variables))


@app.command()
@command
def raw(
    ctx: typer.Context,
    method: str = typer.Argument(..., help="HTTP method (GET only in v1)."),
    path: str = typer.Argument(..., help="API path beginning with /."),
    query: list[str] = typer.Option(None, "--query", help="Repeatable k=v query params."),
):
    """Raw GET passthrough to any API path (read-only)."""
    if method.upper() != "GET":
        raise UsageError("only GET is allowed", hint="pp is read-only in v1")
    params = {}
    for kv in query or []:
        k, _, v = kv.partition("=")
        params[k] = v
    _emit(ctx, rawapi.get(from_session(), path, params=params or None))


@app.command()
@command
def attendance(ctx: typer.Context):
    """Class attendance stats (week, month, year, all-time)."""
    c = from_session()
    client_uuid = _client_uuid(None)
    user_uuid = session.load().user_uuid
    _emit(ctx, attendanceapi.get_attendance_stats(c, client_uuid, user_uuid))


@app.command()
@command
def appointments(
    ctx: typer.Context,
    types: bool = typer.Option(False, "--types", help="List available appointment types."),
    packages: bool = typer.Option(False, "--packages", help="List available packages."),
    credits: bool = typer.Option(False, "--credits", help="Remaining credits per type."),
    history: bool = typer.Option(False, "--history", help="Past appointments."),
):
    """Appointments: upcoming reservations, types, packages, credits, or history."""
    c = from_session()
    if types:
        _emit(ctx, apptapi.appointment_types(c))
    elif packages:
        _emit(ctx, apptapi.appointment_packages(c))
    elif credits:
        _emit(ctx, apptapi.appointment_credit_counts(c, session.load().user_uuid))
    elif history:
        _emit(ctx, apptapi.appointment_history(c, session.load().user_uuid))
    else:
        _emit(ctx, apptapi.upcoming_reservations(c))


@app.command()
@command
def events(
    ctx: typer.Context,
    start_date: str = typer.Option(None, "--start-date", help="Start date YYYY-MM-DD (default today)."),
    end_date: str = typer.Option(None, "--end-date", help="End date YYYY-MM-DD (default +6 months)."),
):
    """Events calendar."""
    from datetime import date as dt, timedelta
    c = from_session()
    sd = start_date or dt.today().isoformat()
    ed = end_date or (dt.today() + timedelta(days=180)).isoformat()
    _emit(ctx, eventsapi.get_events(c, sd, ed))


@app.command()
@command
def preorders(ctx: typer.Context):
    """Merchandise / product preorders."""
    c = from_session()
    user_uuid = session.load().user_uuid
    _emit(ctx, preorderapi.get_preorders(c, user_uuid))


@app.command()
@command
def describe(ctx: typer.Context, name: str = typer.Argument(None, help="Command to describe.")):
    """Emit the capability catalog for agent discovery."""
    if name is None:
        _emit(ctx, describemod.catalog())
        return
    entry = describemod.for_command(name)
    if entry is None:
        raise NotFoundError(f"no such command: {name}")
    _emit(ctx, entry)
