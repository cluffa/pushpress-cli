# PushPress Members API — endpoint map

A sanitized reference map of the **PushPress Members API** (`api.pushpress.com`),
the backend behind the PushPress member apps. This is the detailed companion to
the overview in the [README](../README.md#how-the-pushpress-members-api-works).

Everything here was recovered from the public member apps (Flutter mobile app +
`members.pushpress.com` web build) and confirmed against an account the author
owns. All values are **placeholders** — no tokens, keys, UUIDs, or personal data.

> **Unofficial & undocumented.** Not produced or endorsed by PushPress. The API
> can change without notice. Read-only, own-account use only.

## Conventions

- **Host:** `https://api.pushpress.com` (one host for everything below).
- **Auth:** `Authorization: Bearer <JWT>` on every authenticated call. The mobile
  app also sends `X-Api-Version`; the web app omits it and the API accepts that.
- Path params in `{braces}` come from the token payload (`/v2/auth/verify`).
- `<uuid>`, `<jwt>`, `<user>` etc. are placeholders.

## Hosts

| Host | Role | Needed for member reads? |
|---|---|---|
| `api.pushpress.com` | Main API (REST + GraphQL) | **Yes** |
| `asset.member-app.pushpress.com` | Signed asset/image host | No |
| `trainapi.pushpress.com` | Train product API | No |
| `rank-tracker-api.pushpress.com` | Rank tracker | No |
| `committedclub.pushpress.com` | Committed Club | No |
| `cdn.growthbook.io/api/features/<sdk-key>` | Feature flags (GrowthBook) | No |

## 1. Authentication

Two login paths converge on the same bearer JWT.

### Web (password) — implemented by `pp`

| Method | Path | Body | Returns |
|---|---|---|---|
| `POST` | `/v2/auth/login` | `{ "email", "password" }` | Access data incl. `accessToken` (the JWT), `clientUuid`, `userUuid`, `company`, `subdomain`, `tokenExpiration`. |

### Mobile (passwordless OTP)

| Step | Method | Path | Purpose |
|---|---|---|---|
| 1 | `POST` | `/v2/auth/token/public/access/` | Anonymous app/bootstrap token. |
| 2 | `POST` | `/auth/generate-code` | Send OTP (email/SMS). |
| 3 | `POST` | `/auth/login-with-code` or `/v2/auth/verify` | Exchange OTP. |
| 4 | `POST` | `/v2/auth/token/access/user` | Issue authenticated user JWT (`AuthenticateUser`). |

### Verify / introspect a token

| Method | Path | Returns |
|---|---|---|
| `GET` | `/v2/auth/verify/{jwt}` | `{ isValid, payload: { clientUuid, originClientUuid, userUuid/sub, role, exp, iat, permissions } }`. Token is in the **URL path**, not a header/body. |

The JWT is long-lived (~60 days). The web app stores the access data in a Hive
box `auth_box`, key `clientAccessData-<clientUuid>`.

## 2. REST reads

All `200` with a valid bearer token, `401` without. `{clientUuid}` comes from the
token payload.

| Method | Path | Returns |
|---|---|---|
| `GET` | `/v2/client/client/{clientUuid}` | Gym/company config. |
| `GET` | `/v2/client/client/{clientUuid}/features` | ~28 boolean feature flags. |
| `GET` | `/v2/client/client/{clientUuid}/setting?type={type}[&name={name}]` | Paginated settings envelope. Types: `core`, `train`, `pushpress-membersportal`. |
| `GET` | `/v2/social-feed/feedActivity?gymId={clientUuid}&offset=0&limit=N` | GetStream-format activity feed. |

### Response skeletons (keys only, values stripped)

`GET /v2/client/client/{clientUuid}`:

```jsonc
{
  "id", "uuid", "active", "bankConnected", "company", "email",
  "currencyIso", "gymType", "businessLicense", "joinTimestamp",
  "phone", "addressLine1", "addressLine2", "subdomain", "city", "url",
  "state", "country", "countryIso2", "countryIso3", "countryName", "postalCode",
  "latitude", "longitude", "timezone", "gmtOffset", "timezoneOffset",
  "defaultGatewayId", "stripeUserId", "logoUrl", "salesTrackingId",
  "isMassEmailEnabled", "planType", "spaceId", "externalUuid", "clientSubtypeUuid"
}
```

`GET …/features` → flat map of boolean flags, e.g.:

```jsonc
{ "appointments", "calendarV2", "public_cal_v2_enabled",
  "priority_booking_feature_flag", "hybrid_plans_feature_flag",
  "short_lived_token_feature_flag", "…": true }
```

`GET …/setting?type=…` → paginated envelope:

```jsonc
{ "page", "limit", "hasMore", "total",
  "data": [ { "id", "client_id", "type", "name", "value",
              "create_timestamp", "update_timestamp", "app_setting" } ] }
```

`GET /v2/social-feed/feedActivity?…` → GetStream format:

```jsonc
{ "activities": [ { "actor": { "id", "data": { "avatar", "name", "role", "gymId" } },
                    "foreign_id", "id", "message", "object", "verb", "time",
                    "latest_reactions", "own_reactions", "reaction_counts", "target" } ],
  "limit", "offset" }
```

## 3. GraphQL

Single endpoint carries the bulk of member data.

```
POST /v2/graph/graphql
Authorization: Bearer <jwt>
Content-Type: application/json

{ "query": "<document>", "variables": { … } }
```

- **Apollo Server, production mode — introspection DISABLED.** You must know the
  operations; the schema cannot be dumped.
- `{ "query": "{__typename}" }` answers even **unauthenticated**; real data needs
  the bearer token.
- Documents are built at runtime in Dart (not grep-able as literals). The
  operations below were recovered by live traffic capture.
- Convention: each root field takes a single `…Input` object argument.

### Operations used by `pp`

| Operation | Root field | Key variables | `pp` command |
|---|---|---|---|
| `GetProfiles` | `getProfile(getProfileInput)` | `clientUuid`, `userUuid` | `profile` |
| `GetClasses` | `getCalendarItems(getCalendarItemsInput)` | `classDate`, `calendarSessionTypeId` | `schedule` |
| `GetClass` | `getCalendarItem(getCalendarItemInput)` | `uuid` | `schedule --class-id` |
| `GetEvents` | `getCalendarItems(getCalendarItemsInput)` | `startDate`, `endDate` | `events` |
| `GetWorkoutTypes` | `getClassTypes(getClassTypesInput)` | `date` | `workouts` |
| `GetWorkoutOfDay` | `getWorkoutOfDay(getWorkoutOfDayInput)` | `date`, class type uuid | `workouts --type-id` |
| `GetWorkoutPart` | `getWorkoutPart(getWorkoutPartInput)` | part uuid, workout uid, score id | `workouts --part-id` |
| `UserScoreHistory` | `userScoreHistory(userScoreHistoryInput)` | `keyword` | `scores --keyword`, `workouts --keyword` |
| `GetWorkoutScores` | (workout scores / leaderboard) | part uuid, `date` | `scores` (leaderboard) |
| `GetBenchmarkWorkouts` | `benchmarkWorkouts(benchmarkWorkoutsInput)` | `type`, `search` | `benchmarks` |
| `GetBenchmarkWorkoutHistory` | (benchmark history) | part uuid | `benchmarks --part-uid` |
| `GetWeightliftingWorkoutHistory` | (weightlifting history) | workout uuid | `benchmarks --workout-uid` |
| `GetAttendanceStats` | `getAttendanceStats` | `clientUuid`, `userUuid` | `attendance` |
| `GetUpcomingReservations` | `getUpcomingReservations` | — | `appointments` |
| `AppointmentTypes` | `getAppointmentTypes` | — | `appointments --types` |
| `AppointmentPackages` | `getAppointmentPackages` | — | `appointments --packages` |
| `AppointmentCreditCounts` | `getUserAppointmentCreditsCount` | `userUuid` | `appointments --credits` |
| `AppointmentHistory` | `getUserAppointmentHistory(getUserAppointmentHistoryInput)` | `userUuid` | `appointments --history` |
| `GetPreorders` | `getPreorders(getPreordersInput)` | `userUuid` | `preorders` |

The full query documents — with field selections and fragments (`ProfileFragment`,
`CoachProfile`, …) — live in [`pp/api/`](../pp/api/), one module per command. Those
files are the authoritative record of each operation's exact request and the
fields returned.

### Additional operations seen in the app (not wrapped by `pp`)

Recovered from the app but outside this read-only client's scope — mostly writes
(booking, cancellation, likes) and areas `pp` doesn't cover yet:

`AuthenticateUser`, `GetBadges`/`GetBadge`, `GetBadgeProgress`, `GetBadgeMembers`,
`ListMemberRanks`, `ListRankSystems`, `GetPlans`, `QuerySubscriptionCancelRequests`,
`GetCompanyStatus`, `SyncCheckins`, `bookUserAppointment`, `checkinUserAppointment`,
`cancelAppointmentSchedule`, `createReservation`/`cancelReservation`,
`createSubscription`/`cancelMembership`, `getAppointmentTypeSchedule`,
`getInvoicePreviewForAppointmentPackage`, `getFilteredClasses`,
`createWorkoutAthlete`, `createWorkoutLike`.

## 4. How this map was produced

Three passes; full detail in the [README](../README.md#how-this-was-mapped).

1. **Static analysis of the Flutter mobile bundle** → base URLs (plaintext
   `.env`), OpenAPI client resource groups, operation IDs, REST path templates.
2. **Web build `main.dart.js`** (grep-able for REST paths) + replaying GETs with a
   real bearer token → REST response shapes.
3. **Live proxy capture** (mitmproxy / HTTP Toolkit with TLS-unpinning, or browser
   CDP) → exact GraphQL operations + response shapes, since introspection is off
   and documents are built at runtime.

The recovered response-model naming (`…200Response`, `…404Response`) implies an
OpenAPI/Swagger spec exists server-side; requesting it from PushPress would be the
authoritative source for the REST contract.
