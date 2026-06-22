# TechMentor AI — Frontend

Next.js 14 (App Router) + TypeScript + Tailwind CSS + shadcn/ui style components,
TanStack Query for server state and Zustand for client state.

## Layout

```
frontend/
├── src/
│   ├── app/                 # App Router (layouts, pages, route groups)
│   │   ├── (auth)/          # Public auth pages (login, register)
│   │   ├── (app)/           # Authenticated app (dashboard, ...)
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   ├── page.tsx         # Landing page
│   │   └── providers.tsx    # Client providers (React Query)
│   ├── components/
│   │   ├── ui/              # shadcn-style primitives (button, card, input, label)
│   │   └── layout/          # SiteHeader, SiteFooter
│   ├── lib/                 # utils, constants, query-client factory
│   ├── services/api.ts      # axios instance + JWT interceptor
│   ├── store/               # zustand stores (auth-store)
│   └── types/               # API DTOs mirroring backend schemas
├── tailwind.config.ts
├── next.config.mjs          # /api rewrite -> FastAPI
├── package.json
└── tsconfig.json
```

## Local dev

```bash
npm install
cp .env.example .env.local     # usually no change needed in dev

npm run dev                    # http://localhost:3000
```

In development, the Next.js rewrites proxy `/api/*` to `http://localhost:8000`
(the FastAPI backend), so the browser sees same-origin requests. In production
this is handled by the reverse proxy (nginx / Azure Front Door).

## Scripts

| Task | Command |
|------|---------|
| Dev server | `npm run dev` |
| Production build | `npm run build` |
| Start built app | `npm start` |
| Lint | `npm run lint` |
| Type-check | `npm run type-check` |
| Format | `npm run format` |

## Phase 1 deliverables

- ✅ Next.js 14 App Router scaffold (TypeScript strict)
- ✅ Tailwind CSS theme (light/dark) + shadcn-style primitives (button, card, input, label)
- ✅ Landing page + placeholder login/register/dashboard
- ✅ Axios client with JWT interceptor + error normalization
- ✅ Zustand auth store (persisted)
- ✅ TanStack Query provider
- ✅ API proxy config (`/api/*` → backend)
- ✅ Shared types mirroring backend DTOs

## Phase 2 deliverables (Firebase Auth)

- ✅ Firebase client SDK (`src/lib/firebase.ts`)
- ✅ Login / register forms (email + Google + GitHub via Firebase)
- ✅ `AuthProvider` + `AuthGuard` for protected routes
- ✅ Axios interceptor injects Firebase ID tokens
- ✅ Backend sync via `POST /api/v1/auth/session`

## Notes

- Firebase holds tokens; the backend only verifies ID tokens and stores user profiles.
- Configure `NEXT_PUBLIC_FIREBASE_*` in `.env.local` (see `.env.example`).
- The `(auth)` and `(app)` route groups let us compose distinct layouts without
  affecting the URL paths.
