# Active-Chess — First Set Completed

This migration establishes the V1 core before importing Chess-Mastery-Academy-V16 content.

## Backend
- Track → Course → Chapter → Lesson data model
- Enrollment and LessonProgress models
- Fixed student role default (`student`)
- Central JWT/password security module
- Auth: register, login, current user
- Learning APIs: tracks, courses, chapters, lessons
- Student enrollment and lesson completion APIs
- Admin create APIs for track/course/chapter/lesson
- CORS configuration
- Alembic migration `0001_active_learning_core`
- Seed script with a small kid-friendly sample course

## Frontend
- Kids UI is the default visual language across the foundation
- Large touch targets, rounded cards, friendly language, stars/mascot styling
- Login + registration
- Auth session handling
- Kids dashboard with tracks, courses and progress
- Responsive mobile/tablet layout
- API client with bearer token handling

## Deliberately NOT migrated yet
Puzzles, master games, analysis board, glossary, old V16 UI, and old localStorage progress are kept out of the V1 core. They should be migrated only after the core flow is tested.

## Run
1. `docker compose up -d postgres`
2. `docker compose run --rm backend alembic upgrade head`
3. `docker compose run --rm backend python seed.py`
4. `docker compose up backend frontend`
5. Open `http://localhost:3000`
