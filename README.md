# JobAssist — AI Job Search & Application Assistant

An AI-powered job search, matching, and application management platform.

## Architecture

```
job-assistant/
├── frontend/    React + TypeScript + Vite + Tailwind + TanStack Query + Zustand
├── backend/     Node.js + Express + TypeScript + Prisma + PostgreSQL + JWT
├── shared/      Shared TypeScript types
└── worker/      (Phase 6) Playwright automation worker
```

## Quick Start

### Prerequisites

- Node.js 18+
- PostgreSQL database
- (Optional) OpenAI API key for AI features

### 1. Clone and install

```bash
git clone <repo-url>
cd job-assistant
npm install
```

### 2. Configure backend

```bash
cp backend/.env.example backend/.env
# Edit backend/.env:
#   DATABASE_URL=postgresql://user:password@localhost:5432/job_assistant
#   JWT_SECRET=your-random-32-char-secret
#   OPENAI_API_KEY=sk-...  (optional)
```

### 3. Set up the database

```bash
# Create the database in PostgreSQL first, then:
npm run prisma:generate --workspace=backend
npm run prisma:push --workspace=backend
```

Or with migrations:
```bash
npm run prisma:migrate --workspace=backend
```

### 4. Start development servers

```bash
# Both frontend and backend (requires concurrently):
npm run dev

# Or individually:
npm run dev --workspace=backend    # http://localhost:3001
npm run dev --workspace=frontend   # http://localhost:5173
```

### 5. Open the app

Visit **http://localhost:5173** → Register → Start searching for jobs.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `JWT_SECRET` | ✅ | Min 32 chars, random secret |
| `FRONTEND_URL` | ✅ | CORS origin (default: http://localhost:5173) |
| `OPENAI_API_KEY` | Optional | Enables AI features |
| `OPENAI_MODEL` | Optional | Default: gpt-4o-mini |
| `PORT` | Optional | Default: 3001 |

### Frontend (`frontend/.env`)

| Variable | Description |
|---|---|
| `VITE_API_URL` | Backend API URL (default: http://localhost:3001/api) |

---

## API Endpoints

### Auth
```
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
POST /api/auth/logout
GET  /api/auth/dashboard/stats
```

### Jobs
```
GET    /api/jobs            Search/filter jobs
GET    /api/jobs/saved      User's saved jobs
GET    /api/jobs/:id        Job details
POST   /api/jobs            Create job (internal)
POST   /api/jobs/:id/save   Save job
DELETE /api/jobs/:id/save   Unsave job
GET    /api/jobs/:id/analyze  AI analysis
```

### Resume
```
GET    /api/resume             List resumes
POST   /api/resume             Upload resume (multipart/form-data)
GET    /api/resume/:id         Get resume
PATCH  /api/resume/:id/default Set as default
DELETE /api/resume/:id         Delete resume
POST   /api/resume/:id/extract-skills  AI skill extraction
```

### Applications
```
GET    /api/applications         List applications
POST   /api/applications         Create application
GET    /api/applications/:id     Get application
PATCH  /api/applications/:id/status  Update status
PATCH  /api/applications/:id         Update application
DELETE /api/applications/:id         Delete application
POST   /api/applications/:id/cover-letter  Generate cover letter
POST   /api/applications/:id/match         Match resume to job
```

---

## Application Status Flow

```
DISCOVERED → SAVED → REVIEW → READY_TO_APPLY → PREPARING
  → USER_REVIEW → USER_SUBMITTED → APPLIED → INTERVIEW → OFFER / REJECTED
```

> ⚠️ The system will NOT automatically mark an application as APPLIED.
> The user must confirm via USER_SUBMITTED first.

---

## Build Phases

- **Phase 1** ✅ Foundation: Auth, DB models, API, Frontend shell
- **Phase 2** Resume parsing (PDF/DOCX)
- **Phase 3** Job source adapters (JobSourceAdapter pattern)
- **Phase 4** AI chat, full job matching
- **Phase 5** Application preparation workflow
- **Phase 6** Playwright automation worker
- **Phase 7** Scheduled searches, notifications
- **Phase 8** Production deployment

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| State | TanStack Query, Zustand |
| Backend | Node.js, Express, TypeScript |
| Database | PostgreSQL + Prisma ORM |
| Auth | JWT + bcrypt |
| AI | OpenAI API (provider-abstracted) |
| Automation | Playwright (Phase 6) |
| Deployment | Vercel (frontend), Render (backend), Neon/Supabase (DB) |

---

## Ethics & Legal

This tool is designed for **user-assisted** job searching only.

- ✅ AI helps you find, analyze, and prepare
- ✅ You review and confirm every application
- ❌ No automated mass applications
- ❌ No CAPTCHA bypass or stealth evasion
- ❌ No fabrication of qualifications or experience
- Only automate sources where permitted by their Terms of Service
