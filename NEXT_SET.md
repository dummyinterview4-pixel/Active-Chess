# Active-Chess — Next Set Completed

## Backend
- Added protected course progress endpoint: `GET /courses/{course_id}/progress`.
- Lesson completion now requires active course enrollment.
- Published-content checks added to learning endpoints.
- Re-enrollment can reactivate a non-active enrollment.
- Added root API endpoint and bumped API version to 0.3.0.
- Added backend import/schema tests.

## Frontend
- Added React Router navigation.
- Added protected routes.
- Added course detail + chapter/lesson map.
- Added lesson page and completion action.
- Added real course progress display for enrolled courses.
- Added kids-first course/lesson UI.
- Added clear navigation back to the adventure dashboard.

## Verified locally
- Python source compilation: `python -m compileall backend`
- Backend import test: `pytest backend/tests`
- Frontend package metadata is configured for `npm start`, `npm test`, and `npm run build`.

## Main flow
Register/Login → Dashboard → Course → Chapter → Lesson → Complete → Progress → Dashboard
