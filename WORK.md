# registration-service — what to build

## Responsibility
**Auth + bookings.** Issues JWTs for the whole platform and handles event registrations.
Database: `registration_db` (collections: `users`, `bookings`).

## Endpoints to implement
### Auth (mounted under `/auth`)
| Method | Path              | Purpose                          | Auth |
|--------|-------------------|----------------------------------|------|
| POST   | `/auth/signup`    | Create account, hash password, issue JWT, publish `user.registered` | none |
| POST   | `/auth/login`     | Verify password, issue JWT       | none |
| POST   | `/auth/refresh`   | Rotate JWT                       | JWT |
| GET    | `/auth/me`        | Whoami from JWT                  | JWT |

### Registrations (mounted under `/registrations`)
| Method | Path                        | Purpose                          | Auth |
|--------|-----------------------------|----------------------------------|------|
| POST   | `/registrations`            | Book ticket: validate event, reserve seat, persist, publish `registration.created` | JWT |
| GET    | `/registrations/me`         | List caller's bookings           | JWT |
| GET    | `/registrations/{id}`       | Booking details                  | JWT (owner) |
| DELETE | `/registrations/{id}`       | Cancel: release seat, mark cancelled, publish `registration.cancelled` | JWT (owner) |
| GET    | `/healthz`                  | Already done                     | none |

## What it stores in Mongo
- `users`: `_id`, `email` (unique), `password_hash`, `role`, `created_at`.
- `bookings`: `_id`, `user_id`, `event_id`, `status` (`confirmed`/`cancelled`), `created_at`, `cancelled_at`.

## How it talks to other services
- **Sync HTTP (outbound)**:
  - `GET  {EVENT_SERVICE_URL}/events/{id}` — verify event exists before booking.
  - `POST {EVENT_SERVICE_URL}/events/{id}/reserve` — atomic seat decrement on booking.
  - `POST {EVENT_SERVICE_URL}/events/{id}/release` — on cancellation.
  - `POST {USER_SERVICE_URL}/users` — create profile after signup (or just publish `user.registered` and let user-service consume; pick one — the event-driven path is preferred).
  Use `httpx.AsyncClient` (already in requirements). Set a 5s timeout. On failure of `/reserve`, do NOT persist the booking.
- **Async (RabbitMQ)** — exchange `events.exchange`:
  - **Publish**: `user.registered` (after signup), `registration.created`, `registration.cancelled`.
  - **Consume**: nothing required for MVP (notification-service handles fan-out).
- **JWT issuance**: sign with `JWT_SECRET`, include `sub` (user id), `role`, `exp`. Other services validate locally — they never call back here.

## Env you already have
`MONGO_URL`, `DB_NAME=registration_db`, `JWT_SECRET`, `RABBITMQ_URL`, `EVENT_SERVICE_URL`, `USER_SERVICE_URL`, `PORT=8000`.

---

## How to run locally

You need the infra stack up. The infra repo orchestrates everything.

### Option A — full stack via infra
```
cd ../infra
bash scripts/up-dev.sh
```
registration-service is at **http://localhost:8003**.
Logs: `docker compose -p events-dev logs -f registration-service`

### Option B — code-reload while iterating
1. Start deps + sibling services in containers:
   ```
   cd ../infra
   docker compose -p events-dev -f compose/docker-compose.yml -f compose/docker-compose.dev.yml up -d mongo rabbitmq user-service event-service
   ```
2. Run registration-service on the host:
   ```
   cd ../registration-service
   python -m venv .venv && source .venv/Scripts/activate
   pip install -r requirements.txt
   export MONGO_URL=mongodb://localhost:27017
   export RABBITMQ_URL=amqp://guest:guest@localhost:5672/
   export EVENT_SERVICE_URL=http://localhost:8002
   export USER_SERVICE_URL=http://localhost:8001
   export DB_NAME=registration_db JWT_SECRET=supersecret SERVICE_NAME=registration-service
   uvicorn app.main:app --reload --port 8000
   ```

## After you change code
```
cd ../infra
docker compose -p events-dev -f compose/docker-compose.yml -f compose/docker-compose.dev.yml up -d --build registration-service
```

## Definition of done
- Signup → login → JWT works end-to-end (`curl http://localhost:8003/auth/...`).
- Booking flow: `POST /registrations` rejects when event is full or missing, succeeds otherwise, leaves `seats_left` correctly decremented in event-service.
- `registration.created` and `registration.cancelled` show up in RabbitMQ UI.
- `/healthz` returns 200.
