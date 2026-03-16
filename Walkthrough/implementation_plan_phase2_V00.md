# Phase 2: Next.js Frontend (Login + Dashboard Skeleton)

## Goal
By the end of this phase, a developer can:
1. Open `http://localhost:3000` → see a polished **Login page**
2. Enter credentials → JWT stored in **httpOnly cookie** (set by BFF) → redirect to Dashboard
3. Dashboard shows a **sidebar + topbar shell** with 4 placeholder metric cards
4. Navigating to `/dashboard` without a cookie **redirects to `/login`** (route guard)

---

## Proposed Changes

### Bootstrap Next.js App
#### [NEW] `frontend/` — Next.js 15 project
```bash
npx create-next-app@latest ./ --typescript --app --eslint --no-tailwind --src-dir --import-alias "@/*"
```
- TypeScript + App Router + ESLint
- No Tailwind (we use MUI)

#### Key packages to install after bootstrap:
```
@mui/material @mui/icons-material @emotion/react @emotion/styled
axios
js-cookie @types/js-cookie
```

---

### BFF Change — Cookie-Based Auth  

> [!IMPORTANT]
> We are switching from `Authorization: Bearer` headers to **httpOnly cookies**.
> This is more secure for browser-based apps — JavaScript cannot read httpOnly cookies,
> so XSS attacks cannot steal the token.

#### [MODIFY] [backend/bff/routers/auth.py](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/bff/routers/auth.py)
- `POST /api/v1/auth/login` → after successful login, **set a `Set-Cookie: access_token=...; HttpOnly; SameSite=Lax`** response header instead of returning the token in the JSON body
- `POST /api/v1/auth/logout` → new endpoint, clears the cookie
- `GET /api/v1/auth/me` → reads token from cookie (not Authorization header)

#### [MODIFY] [backend/bff/dependencies.py](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/bff/dependencies.py)
- [get_current_user()](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/bff/dependencies.py#31-56) → reads JWT from [access_token](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/shared/devhub_shared/auth/jwt_handler.py#64-79) cookie instead of `Authorization: Bearer` header

---

### Next.js Pages & Components

#### [NEW] `frontend/src/app/layout.tsx`
- Root layout: MUI ThemeProvider, CssBaseline, global font (Inter from Google Fonts)

#### [NEW] `frontend/src/app/login/page.tsx`
- Centered card with email + password fields
- On submit: `POST /api/v1/auth/login` → backend sets httpOnly cookie → redirect to `/dashboard`
- Shows error snackbar on wrong credentials

#### [NEW] `frontend/src/app/dashboard/layout.tsx`
- Persistent sidebar (220px) + topbar (64px)
- Sidebar links: Overview, Snippets (Phase 3), Automation (Phase 4), Files (Phase 5)
- Topbar: avatar + display name + logout button

#### [NEW] `frontend/src/app/dashboard/page.tsx`
- 4 metric `Card` components in a MUI `Grid`
- Data fetched from `GET /api/v1/auth/me` for user greeting
- Metric cards are static placeholder data (real data wired in Phase 6)

#### [NEW] `frontend/src/middleware.ts`
- Next.js Edge Middleware for route protection
- If [access_token](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/shared/devhub_shared/auth/jwt_handler.py#64-79) cookie missing → redirect to `/login`
- Protects all `/dashboard/*` routes

#### [NEW] `frontend/src/lib/api.ts`
- Axios instance pre-configured with `baseURL=http://localhost:8000`
- `withCredentials: true` (sends cookies on every request)

#### [NEW] `frontend/src/contexts/AuthContext.tsx`
- React context holding [user](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/bff/dependencies.py#31-56) state (fetched from `/api/v1/auth/me`)
- `logout()` function: calls `POST /api/v1/auth/logout` → redirects to `/login`

---

### Style — MUI Theme
- Dark mode primary palette: Deep Navy `#0F172A`, Cyan accent `#06B6D4`
- Typography: Inter (Google Fonts)
- Sidebar: glassmorphism card effect with subtle border
- Metric cards: gradient tops with icon + number + label

---

## Verification Plan

### Automated / Browser Tests
1. `npm run dev` starts without errors
2. `localhost:3000` redirects to `/login` (route guard)
3. Login with `dev@example.com / devhub2026!` → redirected to dashboard
4. Dashboard renders 4 metric cards + username in topbar
5. Logout → redirected to `/login`, cookie cleared
6. Direct navigation to `/dashboard` without cookie → redirected to `/login`

> [!NOTE]
> Services needed during testing:
> - PostgreSQL (docker): `docker compose up -d postgres`
> - Identity Service: `uvicorn main:app --port 8001`
> - BFF: `uvicorn main:app --port 8000`
> - Frontend: `npm run dev` (port 3000)
