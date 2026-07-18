# pp — PushPress Members API CLI

`pp` is an agent-first, read-only, JSON-first command-line client for the
**PushPress Members API** (`api.pushpress.com`) — the backend behind the
PushPress member apps (the Flutter mobile app `com.pushpress.memberportal` and
the `members.pushpress.com` web build).

It is built for scripting and for use by LLM agents: every command emits
structured JSON to stdout by default, errors are structured JSON on stderr with
a stable exit-code contract, and the whole capability surface is self-describing
via `pp describe`.

> **Built with AI.** This project — the code, tests, and documentation
> (including the API map below) — was written with the assistance of AI
> (Anthropic's Claude). Treat it as a starting point and verify behavior against
> your own account before relying on it.
>
> **Unofficial.** This is an independent, community-built client. It is not
> produced or endorsed by PushPress. The API is undocumented and may change
> without notice. See [Legal & scope](#legal--scope).

- [Install](#install)
- [Authentication](#authentication)
- [Output contract](#output-contract)
- [Commands](#commands)
- [Environment variables](#environment-variables)
- [How the PushPress Members API works](#how-the-pushpress-members-api-works) ← recreate it from scratch
- [Development](#development)
- [Legal & scope](#legal--scope)

---

## Install

```bash
uv tool install .
```

This installs the `pp` entry point on your `PATH`.

For development, run from a checkout without installing:

```bash
uv run pp --help
```

Requires Python ≥ 3.9. Runtime deps: `httpx`, `typer`, `rich`.

## Authentication

Every request carries `Authorization: Bearer <JWT>`. There are three ways to get
one into `pp`:

1. **`PP_TOKEN` env var** — pass a bearer token you already have and skip session
   storage entirely:

   ```bash
   PP_TOKEN=<jwt> pp whoami
   ```

2. **`pp login --token`** — store a pre-obtained bearer token to disk:

   ```bash
   pp login --token <jwt>
   ```

3. **`pp login --email … --password-stdin`** — log in with credentials (this is
   the flow the **web** app uses; see [Auth](#1-authentication) below):

   ```bash
   echo -n 'your-password' | pp login --email you@example.com --password-stdin
   ```

Where do you get a token by hand? Log into `members.pushpress.com` in a browser,
open DevTools, and read the JWT the app stores in the Hive `auth_box`
(`localStorage`/IndexedDB), key `clientAccessData-<clientUuid>`, field
`accessToken`. Tokens are long-lived (~60 days).

Passwords and tokens are never printed. A stored session is written to
`~/.config/pp/session.json` (mode `600`); override the location with
`$PP_CONFIG_DIR` or `$XDG_CONFIG_HOME`. `pp logout` deletes it.

## Output contract

- **JSON by default.** Every command prints a single JSON document to stdout
  (2-space indent).
- **`--human`** — human-readable rendering (falls back to JSON where no
  dedicated renderer exists).
- **`--ndjson`** — for list payloads, stream one JSON object per line.
- **`--fields a,b,c`** — project output down to a set of top-level fields
  (applied per item for lists).
- **Errors** are structured JSON on stderr:
  `{"error", "code", "detail", "hint"}` (`detail`/`hint` omitted when N/A).

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Generic error |
| 2 | Usage error (bad arguments/flags) |
| 3 | Auth required / unauthorized |
| 4 | Not found |
| 5 | Upstream API error |
| 6 | Network error |

## Commands

Run `pp describe` for the machine-readable capability catalog, or
`pp describe <name>` for one command's detail.

| Command | Purpose |
|---|---|
| `login` / `logout` / `whoami` | Session management + token verification. |
| `profile` | Your profile, memberships, and subscriptions. |
| `gym` | Gym / company configuration. |
| `features` | Feature-flag map for the gym. |
| `settings <type>` | Client settings (`core`, `train`, `pushpress-membersportal`). |
| `schedule` | Class schedule for a date, or detail for one class. |
| `workouts` | Class types, workout-of-the-day, workout parts, score history. |
| `scores` | Workout leaderboard or personal score history. |
| `benchmarks` | Benchmark categories, workouts, and history. |
| `attendance` | Check-in / attendance stats (week/month/year/all-time). |
| `appointments` | Upcoming reservations, types, packages, credits, history. |
| `events` | Events calendar. |
| `preorders` | Merchandise / product preorders. |
| `feed` | Gym social feed activity. |
| `graphql` | Raw GraphQL passthrough to `/v2/graph/graphql`. |
| `raw` | Raw GET passthrough to any API path (rejects non-GET). |
| `describe` | Emit the capability catalog for agent discovery. |

Commands that operate on a gym accept `--client-uuid` to override the UUID stored
in the session; otherwise it is read from the session (or resolved from the token
via `/v2/auth/verify`).

### Examples

```bash
pp whoami --fields isValid
pp gym --fields company,timezone
pp schedule --date 2026-07-20
pp workouts --date 2026-07-20
pp scores --keyword "Fran"
pp benchmarks --type WEIGHTLIFTING
pp attendance
pp appointments --types
pp feed --limit 10
pp graphql -q '{__typename}'
pp raw GET /v2/client/client/<uuid>/features
```

## Environment variables

| Var | Purpose |
|---|---|
| `PP_TOKEN` | Bearer token for every request, bypassing the stored session file. |
| `PP_CONFIG_DIR` | Config dir (default `~/.config/pp`, or `$XDG_CONFIG_HOME/pp`). |
| `PP_API_BASE` | API base URL (default `https://api.pushpress.com`). |

`pp` performs **no mutations** — `pp raw` rejects any method other than `GET`.

---

# How the PushPress Members API works

This section is a from-scratch map of the API so you could rebuild this client
(or a different one) without any of the reverse-engineering that produced it.
Everything below was recovered from the public member apps and confirmed against
a live account the author owns; no private or third-party data is included.

> A fuller endpoint-map reference — auth flows, REST response skeletons, the
> complete GraphQL operation table, and additional operations `pp` doesn't wrap —
> lives in [`docs/API.md`](docs/API.md).

## The shape of it

- **One host:** `https://api.pushpress.com`.
- **Two API styles side by side:**
  - a **REST** surface (`/v2/…`) for gym config, settings, feature flags, and
    the social feed;
  - a single **GraphQL** endpoint (`POST /v2/graph/graphql`) that carries the
    bulk of member data — schedule, profile, memberships, workouts, scores,
    benchmarks, attendance, appointments, events, preorders.
- **Auth is a bearer JWT** on every call: `Authorization: Bearer <token>`. No
  other header is strictly required (the mobile app additionally sends
  `X-Api-Version`; the web app does not, and the API accepts requests without
  it).

Other first-party hosts exist for adjacent products but are not needed for member
reads: `trainapi.pushpress.com`, `rank-tracker-api.pushpress.com`,
`committedclub.pushpress.com`, `asset.member-app.pushpress.com` (signed asset
host). Feature flags are served by GrowthBook at
`cdn.growthbook.io/api/features/<sdk-key>`.

## 1. Authentication

There are **two** login paths to the same bearer-token world:

| Client | Flow |
|---|---|
| **Web** (`members.pushpress.com`) | Password login: `POST /v2/auth/login` with `{ "email", "password" }` → returns the access data (incl. `accessToken`). |
| **Mobile** (Flutter app) | Passwordless OTP: `POST /auth/generate-code` (send code), then `POST /auth/login-with-code` / `POST /v2/auth/verify` to exchange it, then `POST /v2/auth/token/access/user` to issue the user JWT. |

`pp` implements the **web password flow** (`pp login --email …`). Either way you
end up with a JWT.

**Verify / introspect a token** (no body, token goes in the *path*):

```
GET /v2/auth/verify/{token}
→ { "isValid": bool,
    "payload": { "clientUuid", "originClientUuid", "userUuid"/"sub",
                 "role", "exp", "iat", "permissions": { … } } }
```

`pp whoami` is exactly this call. It is also how `pp` resolves your
`clientUuid`/`userUuid` when all you have is a raw token.

**Token storage in the apps.** The web app persists the access data in a Hive box
`auth_box` under key `clientAccessData-<clientUuid>`:

```jsonc
{
  "clientUuid": "client_…",
  "userUuid":   "…",
  "company":    "Your Gym",
  "subdomain":  "yourgym",
  "logoUrl":    "…",
  "privileges": ["feed.activity.view", "feed.user.update"],
  "accessToken": "<JWT>",           // the bearer token
  "tokenExpiration": "2026-09-15T…" // ~60-day lifetime
}
```

## 2. REST reads

All return `200` with a valid bearer token and are `401` without one. `{clientUuid}`
comes from the token payload.

| Method / Path | Returns |
|---|---|
| `GET /v2/client/client/{clientUuid}` | Gym/company config: name, address, `timezone`, `currencyIso`, `gymType`, `logoUrl`, Stripe linkage, etc. |
| `GET /v2/client/client/{clientUuid}/features` | ~28 boolean feature flags (`appointments`, `calendarV2`, `hybrid_plans_feature_flag`, …). |
| `GET /v2/client/client/{clientUuid}/setting?type={type}[&name={name}]` | Paginated settings envelope `{ page, limit, hasMore, total, data: [ … ] }`. Types: `core`, `train`, `pushpress-membersportal`. |
| `GET /v2/social-feed/feedActivity?gymId={clientUuid}&offset=0&limit=N` | GetStream-format feed: `{ activities: [ { actor, verb, object, message, time, reaction_counts, … } ], limit, offset }`. |

`pp gym`, `pp features`, `pp settings`, and `pp feed` are thin wrappers over these
four.

## 3. GraphQL — the bulk of member data

Everything member-specific goes through one endpoint:

```
POST /v2/graph/graphql
Authorization: Bearer <token>
Content-Type: application/json

{ "query": "<document>", "variables": { … } }
```

Facts worth knowing before you build against it:

- It is **Apollo Server in production mode** — **introspection is disabled**, so
  you cannot dump the schema. You must know the operations you want.
- A trivial query works **even unauthenticated**: `{ "query": "{__typename}" }`
  → `{ "data": { "__typename": "Query" } }`. Real data queries require the bearer
  token.
- The apps build query documents programmatically in Dart, so they are **not
  grep-able as string literals** in the app bundles. The exact documents were
  recovered by capturing live traffic (see [How this was mapped](#how-this-was-mapped)).

The operations `pp` uses (all queries; each takes a single `…Input` object as its
argument — a common PushPress convention), grouped by command:

| `pp` command | GraphQL operation → root field | Key variables |
|---|---|---|
| `profile` | `GetProfiles` → `getProfile(getProfileInput)` | `clientUuid`, `userUuid` |
| `schedule` (list) | `GetClasses` → `getCalendarItems(getCalendarItemsInput)` | `classDate` (also `calendarSessionTypeId`) |
| `schedule --class-id` | `GetClass` → `getCalendarItem(getCalendarItemInput)` | `classId`/`uuid` |
| `events` | `GetEvents` → `getCalendarItems(getCalendarItemsInput)` | `startDate`, `endDate` |
| `workouts` (types) | `GetWorkoutTypes` → `getClassTypes(getClassTypesInput)` | `date` |
| `workouts --type-id` | `GetWorkoutOfDay` → `getWorkoutOfDay(getWorkoutOfDayInput)` | `date`, class type uuid |
| `workouts --part-id` | `GetWorkoutPart` → `getWorkoutPart(getWorkoutPartInput)` | part uuid, workout uid, score id |
| `scores` / `workouts --keyword` | `UserScoreHistory` → `userScoreHistory(userScoreHistoryInput)` | `keyword` |
| `scores` (leaderboard) | `GetWorkoutScores` | part uuid, `date` |
| `benchmarks` (find) | `GetBenchmarkWorkouts` → `benchmarkWorkouts(benchmarkWorkoutsInput)` | `type`, `search` |
| `benchmarks --part-uid` | `GetBenchmarkWorkoutHistory` | part uuid |
| `benchmarks --workout-uid` | `GetWeightliftingWorkoutHistory` | workout uuid |
| `attendance` | `GetAttendanceStats` → `getAttendanceStats` | `clientUuid`, `userUuid` |
| `appointments` (default) | `GetUpcomingReservations` → `getUpcomingReservations` | — |
| `appointments --types` | `AppointmentTypes` → `getAppointmentTypes` | — |
| `appointments --packages` | `AppointmentPackages` → `getAppointmentPackages` | — |
| `appointments --credits` | `AppointmentCreditCounts` → `getUserAppointmentCreditsCount` | `userUuid` |
| `appointments --history` | `AppointmentHistory` → `getUserAppointmentHistory(getUserAppointmentHistoryInput)` | `userUuid` |
| `preorders` | `GetPreorders` → `getPreorders(getPreordersInput)` | `userUuid` |

The full query documents (with field selections and fragments like
`ProfileFragment` and `CoachProfile`) live in
[`pp/api/`](pp/api/) — one module per command. Read those files for the exact
shape you'll get back; they are the authoritative record of each operation.

A minimal request in `curl`:

```bash
curl -s https://api.pushpress.com/v2/graph/graphql \
  -H "Authorization: Bearer $PP_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"query":"query GetProfiles($clientUuid:String!,$userUuid:String!){profile:getProfile(getProfileInput:{clientUuid:$clientUuid,userUuid:$userUuid}){userUuid firstName lastName __typename} __typename}","variables":{"clientUuid":"client_…","userUuid":"…"}}'
```

## How this was mapped

The app is a **Flutter** app compiled to an AOT Dart snapshot (`libapp.so`), so
there is no readable API logic in Java/Kotlin. The map above was assembled from
three passes:

1. **Static analysis of the mobile bundle.** The APK's `assets/flutter_assets/`
   ships a plaintext `.env` (base URLs + public SDK keys). String/symbol
   extraction from the Dart snapshot recovered the OpenAPI-generated client's
   resource groups (`*Api` classes) and operation IDs — enough to know *what*
   exists and the REST path templates. (A full Dart decompile via `blutter`
   needs an arm64 build of the snapshot.)
2. **The web build.** `members.pushpress.com` serves `main.dart.js`
   unminified enough to grep for **REST paths** (architecture-independent, unlike
   the arm32 mobile snapshot). Replaying those GETs with a real bearer token from
   the page context yields the REST response shapes.
3. **Live capture for GraphQL.** Because the GraphQL documents are built at
   runtime and introspection is disabled, the only way to get exact operations +
   response shapes is to observe real traffic — an HTTPS-intercepting proxy
   (mitmproxy / HTTP Toolkit) with TLS-pinning bypass (Frida / reFlutter) on the
   mobile app, or CDP/DevTools network capture in the browser. Every GraphQL
   operation `pp` uses was captured this way against the author's own account.

The response-model naming in the recovered client (`…200Response`,
`…404Response`) strongly implies an OpenAPI/Swagger spec exists server-side; if
you want an authoritative REST contract, requesting it from PushPress is more
reliable than any of the above.

## Recreating the client

With the token and the map above, a minimal client is:

1. Get a bearer token (web password login, or copy it out of a logged-in
   session — see [Authentication](#authentication)).
2. `GET /v2/auth/verify/{token}` to learn your `clientUuid` and `userUuid`.
3. For gym config / settings / features / feed → the [REST reads](#2-rest-reads).
4. For everything member-specific → `POST /v2/graph/graphql` with the
   [operations above](#3-graphql--the-bulk-of-member-data).

That is exactly what `pp` does; the source in [`pp/`](pp/) is small and readable
if you want a reference implementation.

---

## Development

```bash
uv run pytest          # 98 tests, all offline (HTTP mocked with respx)
uv run pp --help
```

Layout:

```
pp/
├── cli.py         # Typer command definitions + output flags
├── http.py        # PPClient: bearer auth, error → exit-code mapping
├── session.py     # token storage / resolution
├── config.py      # config dir + session path
├── models.py      # Session model
├── output.py      # JSON / ndjson / --fields / --human emit layer
├── errors.py      # PPError hierarchy with stable codes
├── describe.py    # self-describing capability catalog
└── api/           # one module per resource; GraphQL docs live here
```

## Legal & scope

Built for **interoperability and access to your own data**. It talks to your
account with your own credentials and performs **read-only** requests. Do not use
it to access accounts or data you are not authorized to, and respect PushPress's
Terms of Service. This project is unofficial and unaffiliated with PushPress; the
API is undocumented and may change or break at any time.

Licensed under the [MIT License](LICENSE).
