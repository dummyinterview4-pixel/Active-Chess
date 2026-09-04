# Active-Chess — Set 7 Planning

Written after an independent verification pass on the Set 6 deliverable
(not just a source read — the backend was actually booted, migrated, and
hit with live requests; the frontend was actually built).

## Verified working (Set 1–6), confirmed by running the app
- Full Alembic migration chain runs clean: `alembic upgrade head` seeds
  2 tracks, 7 courses, 24 lessons, 113 puzzles, 44 master games from the
  V16 dataset.
- Auth (register/login/JWT) → enroll → course progress flow works end to end.
- Puzzles, quizzes, gamification (stars/streaks/badges), profile, master
  games, and the parent/coach dashboards all respond correctly with real data.
- Frontend builds clean (`npm run build`, zero warnings).
- Production `docker-compose.prod.yml` correctly requires `SECRET_KEY`,
  `DB_PASSWORD`, etc. via `${VAR:?required}` guards.

## Fixed in this pass (see git history / diffs)
- Removed 4 dead/orphaned route files (`enrollments.py`, `tutorials.py`,
  `chapters.py`, `courses.py`) that were never wired into `main.py`; two of
  them (`enrollments.py`, `tutorials.py`) referenced `Coupon`/`Tutorial`
  model classes that don't exist and would have raised `ImportError` if
  ever imported. Their presence confirmed the **V16 coupon system was never
  migrated** — it's not on the Set 6 checklist and there's no coupon model,
  schema, or endpoint anywhere in the current app.
- Added `.gitignore` (none existed at any level in this repo).
- Fixed the one ESLint warning from `npm run build` (missing `useEffect`
  dependency in `MasterGamesPage.jsx`).
- Corrected `TODO.md`: "V16 content import mapping" was already implemented
  (in the `20260904_seed_v16_content` migration) but was still marked
  unchecked.
- Added 6 real API integration tests (`tests/test_api_integration.py`) that
  boot the actual app against an in-memory DB and exercise register/login/
  enroll/progress/master-games/auth-rejection — the previous 2 tests only
  grepped source text and instantiated a schema, so they couldn't catch
  wiring regressions like the dead files above.

## Carried over from Set 6's own "Next set" list
- [x] Real chessboard interaction with legal move validation. Added
      `chess.js` + `react-chessboard` to the frontend and built
      `PuzzleChessBoard` (drag-and-drop + click-to-move, legal-move
      highlighting) wired into `PuzzleLesson`. Submits the resulting SAN
      move to the existing `/puzzles/{id}/attempt` endpoint — the backend
      remains the sole authority on correctness, so no server-side puzzle
      logic changed.
- [ ] Rich master-game replay using a real chess rules library (current
      `GameViewer` just steps through a whitespace-split move-token string;
      V16's `GameReplayer` used `chess.js` for a live board).
- [ ] Parent/coach notifications and assignments.
- [ ] Course recommendation tuning by age, level, and puzzle performance
      (current `/me/recommendations` logic is a first pass).
- [ ] Expanded automated API integration test coverage (this pass added a
      baseline — extend to puzzles/quizzes/badges/admin/coach/parent routes).

## New from this verification pass — decided
- [x] **Coupon system**: decision made — migrate it. Added a `Coupon`
      model, `EnrollmentCreate.coupon_code`, validation in the enroll
      endpoint (only for paid courses, `fee > 0`), and admin-only
      `/admin/coupons` management endpoints. `FREE` seeded with unlimited
      redemptions via `20260904_add_coupons` migration.
- [ ] No rate limiting on `/auth/login` or `/auth/register` (V16's backend
      had a `limiter.py`/slowapi setup; the new backend has none). Low
      priority unless this goes properly public before launch.
- [ ] Backend `pydantic`/SQLAlchemy versions trigger deprecation warnings
      (`declarative_base()`, class-based `Config`) — not urgent, but worth
      a version bump pass at some point so warnings don't become errors on
      a future dependency upgrade.
