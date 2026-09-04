# Active-Chess Architecture

## Learning hierarchy

Track → Course → Chapter → Lesson → LessonProgress

## Frontend

- `app`: bootstrapping and routes
- `components`: reusable UI/layout/chess primitives
- `features`: user-facing domain behaviour
- `pages`: route-level composition only
- `services`: API communication
- `store`: small cross-feature state
- `styles`: design system and themes

## Backend

- `core`: configuration/security
- `db`: database/session/migrations
- `models`: persistence entities
- `schemas`: API contracts
- `routes`: HTTP endpoints
- `services`: business rules

## Future content

Puzzles, master games, analysis and AI are separate modules. They should attach to the learning experience without becoming the core Course → Chapter → Lesson hierarchy.
