# Active-Chess

Kids-first chess learning platform migrated from Chess-Mastery-Academy-V16.

## Current flow
`Register/Login → Dashboard → Course → Chapter → Lesson → Complete → Progress`

## Run with Docker
```bash
docker compose up --build
```
Then:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

After the database is ready, seed the starter content:
```bash
docker compose exec backend python seed.py
```

## Current migration sets
- Set 1: learning-core backend + kids UI foundation.
- Set 2: routing, protected screens, course/lesson flow, enrollment-aware progress, lesson completion and tests.


## Set 6 — Family, Coaching & Master Games
- Parent and coach dashboards with role-based access.
- V16 master game library with step-through replay.
- Parent/student relationship support.
- Personalized next-course recommendations.
- Production security configuration guards.

### Expanded flow
`Register/Login → Dashboard → Recommendation → Course → Chapter → Lesson → Progress`
`Parent → Family Dashboard → Student Progress`
`Coach → Coach Dashboard → Student Progress`
`Dashboard → Master Games → Move-by-Move Study`
