# CampusBite

Food ordering for a university campus, from the menu to the hostel door.

Students order from campus restaurants. Kitchens manage menus and move orders along, and couriers handle the last stretch. There's also a small AI assistant that answers questions about your own order history ("what did I spend this week?").

Built with **FastAPI + SQLAlchemy + PostgreSQL** on the backend and **React + Vite** on the frontend. The API runs in Docker Compose.

---

## What it does

There are three kinds of account. Each one sees a different part of the app.

**Students (customers)**
- Browse restaurants with search, pagination and average ratings
- Open a menu and filter by name, price range and availability, then sort by name or price
- Fill a basket (one restaurant at a time; it survives a page refresh) and check out with a test card. No real payment happens. The order is marked `mock_paid` and a ledger entry is written.
- Follow an order on a step-by-step timeline, along with its payment ledger
- Cancel while the order is still `PLACED` (the payment is reversed automatically)
- Once it's delivered, leave a 1–5 star review or ask for a refund (one of each per order)
- Ask the AI assistant about past orders

**Kitchens (restaurant owners)**
- Signing up as an owner creates your restaurant at the same time
- Overview: total and today's orders, revenue, refunds, rating, a status breakdown and best-selling dishes
- Stale-order alerts: anything sitting in `PLACED` or `ACCEPTED` for 15+ minutes gets flagged by a background watcher. You can dismiss an alert or re-scan on demand.
- Menu editor: add, edit and remove dishes (removal is soft, so old orders stay intact) and toggle availability
- Order queue: accept, start preparing, mark ready or reject, then hand a ready order to a courier
- Refund desk: approve (writes a refund ledger entry and marks the order `REFUNDED`) or reject, with an optional note

**Couriers (delivery partners)**
- See assigned deliveries with the customer's name, phone, address and items
- Mark an order as picked up (`OUT_FOR_DELIVERY`), then `DELIVERED`
- Browse past deliveries

### How an order moves

```
PLACED ─▶ ACCEPTED ─▶ PREPARING ─▶ READY ─▶ ASSIGNED ─▶ OUT_FOR_DELIVERY ─▶ DELIVERED
  │                                                                          │
  └─▶ CANCELLED                                          refund approved ─▶ REFUNDED
```

- The kitchen drives everything up to `READY`. Assigning a courier moves the order to `ASSIGNED`.
- Only the assigned courier can move it past that.
- Only a `PLACED` order can be cancelled, by either the student or the kitchen.
- A skipped step returns `400`. The wrong person trying a step gets `403`.

The rules are a single transition table in `backend/app/domain/lifecycle.py`.

### Access control

Every protected endpoint declares the roles it accepts (`roles_allowed(...)` in `backend/app/api/auth_guards.py`), and ownership is checked on top of that:
- Students only ever see their own orders. Someone else's order looks like a `404`.
- Kitchens only touch their own restaurant.
- Couriers only see deliveries assigned to them.

Passwords are stored as bcrypt hashes. Login returns an HS256 JWT, which the frontend keeps in `localStorage` and attaches through an axios interceptor. A `401` signs you out.

### AI assistant

`POST /api/ai/insights` takes an optional `question`. If you leave it out, you get a summary.

The backend collects the caller's 50 most recent orders, and only theirs, as JSON. It sends them to OpenAI (default model `gpt-4o-mini`) and returns the reply. The API key stays on the server.

| Situation | Response |
|---|---|
| No key, or an invalid key | `503` |
| OpenAI rate limit | `429` |
| Any other OpenAI error | `502` |
| More than `AI_RATE_LIMIT_PER_MINUTE` requests (default 5) from one user in a minute | `429` with `Retry-After` |

### Under the hood
- **Request tracing:** a small ASGI middleware logs every request and adds the `X-Request-ID` and `X-Process-Time` headers.
- **Stale-order watcher:** starts with the app and sweeps every `REMINDER_INTERVAL_SECONDS`. It raises at most one alert per order and status, and clears the alert once the order moves on.

---

## Getting it running

You need Docker (with Compose) and Node 18+.

**API + database**

```bash
cp .env.example .env        # fill in POSTGRES_PASSWORD and JWT_SECRET (OPENAI_API_KEY is optional)
docker compose up --build
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

The container loads demo data on first boot and skips it if accounts already exist. Run `docker compose down -v` to wipe the database.

**Web app**

```bash
cd frontend
cp .env.example .env        # VITE_API_URL=http://localhost:8000/api
npm install
npm run dev                 # http://localhost:5173
```

`npm run build` produces a static bundle in `frontend/dist/`.

**Without Docker**

The backend falls back to SQLite:

```bash
cd backend
python3.12 -m venv ../.venv && source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.demo_data
uvicorn app.server:app --reload
```

### Demo logins

The password for every demo account is `password123`. The sign-in page has one-click buttons for all of them.

| Who | Email | Notes |
|---|---|---|
| Student | `customer@campusbite.app` | Ishaan, has order history |
| Student | `customer2@campusbite.app` | Ananya |
| Kitchen | `owner@campusbite.app` | Tandoor Junction |
| Kitchen | `owner2@campusbite.app` | Forno Rosso |
| Kitchen | `owner3@campusbite.app` | Bamboo Basket |
| Kitchen | `owner4@campusbite.app` | Leaf & Ladle |
| Courier | `partner@campusbite.app` | Arjun |
| Courier | `partner2@campusbite.app` | Kavya |

Tandoor Junction starts with one live order at every stage plus one stale `PLACED` order, so the alerts panel isn't empty on first login.

### Tests

```bash
cd backend
pytest -q
```

Tests are grouped by feature:
- auth and access control
- checkout and the order lifecycle
- reviews and refunds
- listing filters and pagination
- the stale-order watcher
- the AI endpoint (OpenAI is mocked; the tests check that only the caller's orders are sent)
- platform concerns: health check, tracing headers, the rate limit and the seed

---

## Code map

```
backend/app/
  server.py            app factory: middleware, routers, watcher lifespan
  demo_data.py         seed script
  core/                settings, db session, clock, passwords, JWT, request tracing
  models/              SQLAlchemy models (accounts, catalog, orders, alerts)
  schemas/             Pydantic request/response models
  domain/              business logic: lifecycle, checkout, payments, stats,
                       listing helpers, stale-order watcher, insights engine
  api/                 routers + auth guards
backend/tests/         pytest suite (fixtures in conftest.py, helpers in support.py)

frontend/src/
  app/                 routes, shell layout, sidebar, route guards
  services/            axios instance + one module per API area
  state/               SessionProvider, BasketProvider
  lib/                 formatting, status metadata, small hooks
  ui/                  shared components (OrderTimeline, StatusPill, Dialog, Pager…)
  features/            auth, browse, customer, owner, courier screens
  styles/              design tokens + layered stylesheets
```

### Data model

| Table | Holds |
|---|---|
| `accounts` | every user, with a role |
| `restaurants` | one per owner |
| `menu_entries` | dishes, with availability and a soft-delete flag |
| `orders` | order status, payment status, refund status, total, courier |
| `order_lines` | items, storing the dish name and price as they were when ordered |
| `ledger_entries` | `payment` and `refund` movements |
| `reviews` | one per order |
| `return_claims` | refund requests, one per order |
| `stale_order_alerts` | watcher output |

Tables are created on startup.

---

## Configuration

**Root `.env`** (used by Docker Compose)

| Variable | What it's for | Default |
|---|---|---|
| `POSTGRES_USER` | Database user | `campusbite` |
| `POSTGRES_PASSWORD` | Database password | — |
| `POSTGRES_DB` | Database name | `campusbite` |
| `JWT_SECRET` | Token signing key | — |
| `JWT_EXPIRE_MINUTES` | How long a token is valid | `1440` |
| `OPENAI_API_KEY` | Enables the AI assistant | — |
| `OPENAI_MODEL` | Model to use | `gpt-4o-mini` |
| `AI_RATE_LIMIT_PER_MINUTE` | AI requests allowed per user per minute | `5` |
| `CORS_ORIGINS` | Allowed frontend origins, comma-separated | `http://localhost:5173` |
| `REMINDER_THRESHOLD_MINUTES` | Minutes before an order counts as stale | `15` |
| `REMINDER_INTERVAL_SECONDS` | How often the watcher runs | `60` |

- Compose assembles `DATABASE_URL` itself. Outside Docker, set `DATABASE_URL` in `backend/.env`.
- The frontend only needs `VITE_API_URL`.
- Real `.env` files are git-ignored and excluded from the Docker image.

---

## API at a glance

Everything lives under `/api`. Interactive docs are at `/docs`.

| Area | Endpoints |
|---|---|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Browsing | `GET /restaurants`, `GET /restaurants/{id}`, `GET /restaurants/{id}/menu`, `GET /restaurants/{id}/reviews` |
| Student orders | `POST /orders`, `GET /orders/my`, `GET /orders/{id}`, `POST /orders/{id}/cancel`, `POST /orders/{id}/review`, `POST /orders/{id}/return` |
| Kitchen | `GET/PUT /owner/restaurant`, `GET/POST /owner/menu`, `PUT/DELETE /owner/menu/{id}`, `PATCH /owner/menu/{id}/availability`, `GET /owner/orders`, `PATCH /owner/orders/{id}/status`, `GET /owner/delivery-partners`, `POST /owner/orders/{id}/assign`, `GET /owner/stats` |
| Refunds | `GET /owner/returns`, `POST /owner/returns/{id}/approve`, `POST /owner/returns/{id}/reject` |
| Alerts | `GET /owner/reminders`, `POST /owner/reminders/refresh`, `POST /owner/reminders/{id}/dismiss` |
| Couriers | `GET /delivery/orders`, `PATCH /delivery/orders/{id}/status`, `GET /delivery/history` |
| AI | `POST /ai/insights` |

**List filters.** List endpoints take `page` and `page_size`.
- Order lists also accept `status`, `date_from` and `date_to`.
- The menu accepts `search`, `min_price`, `max_price`, `available_only` and `sort`.

**Error codes**

| Code | Meaning |
|---|---|
| `400` | Business rule broken |
| `401` | Not signed in |
| `403` | Wrong role |
| `404` | Missing, or not yours |
| `409` | Duplicate (email, review or refund request) |
| `422` | Validation failed |
| `429` | Rate limited |
| `502` / `503` | AI service trouble |

---

## Deploying

- **Backend:** the image is self-contained. Give it a managed Postgres through `DATABASE_URL` plus the variables above (works on Render, Railway, Fly.io and similar).
- **Frontend:** build with `VITE_API_URL` set to the deployed API and host `frontend/dist` on Netlify or Vercel.
- Add the frontend's URL to `CORS_ORIGINS`.
