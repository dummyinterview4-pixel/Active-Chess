# Active-Chess TODO

## Completed
- [x] Learning core data model
- [x] JWT authentication
- [x] Tracks and published courses API
- [x] Enrollment API
- [x] Lesson progress API
- [x] Enrollment required for lesson completion
- [x] Course progress API
- [x] Kids UI foundation
- [x] React Router + protected routes
- [x] Course detail / chapter / lesson map
- [x] Lesson completion screen
- [x] Dashboard course progress
- [x] Backend smoke/schema tests

## Next migration set
- [x] Admin content-management UI
- [x] Parent/coach dashboard roles
- [x] V16 content import mapping (verified: `alembic upgrade head` seeds 7 courses, 24 lessons, 113 puzzles, 44 master games from `v16_content.json`)
- [x] Puzzle engine
- [x] Master games
- [x] Chessboard lesson activities
- [x] Badges/stars and streaks
- [x] Course recommendations by age/level
- [x] Production security configuration

## Set 5 (completed)
- [x] Quiz engine (QuizQuestion/QuizAttempt models, routes, kid-facing QuizLesson UI)
- [x] Stars/streak/badge persistence (UserStats, Badge, UserBadge + gamification service)
- [x] Child profile with avatar picker (ChildProfile model, /me/profile routes, ProfilePage UI)
- [x] Coach UI to create/edit/delete puzzles and quiz questions (Content Studio in /admin)
- [x] Fixed pre-existing schema drift: enrollments.completed_at column was missing from migrations
- [x] Wired PuzzleLesson/QuizLesson into LessonPage by lesson_type (previously built but never connected)

## Set 6 (completed)
- [x] Parent role and parent/student linking
- [x] Coach/admin student dashboard
- [x] Parent progress dashboard
- [x] Dedicated V16 master game library and replay UI
- [x] Course recommendation API/UI
- [x] Production SECRET_KEY and database configuration guards
- [x] Coach/trainer access to Content Studio

## Set 7 (this update)
- [x] **Coupon system migrated** (decision made: yes). Re-scoped from V16's
      signup-level gate to enrollment-level, matching active-chess's
      per-course `fee` model: a coupon is only required when
      `course.fee > 0`; free courses are unaffected. Real `Coupon` table
      (code, active flag, redemption cap/counter), `Enrollment.coupon_code`
      records what was redeemed, admin-only (not coach/trainer) management
      endpoints, `FREE` seeded with unlimited redemptions.
- [x] Real chessboard interaction (`chess.js` + `react-chessboard`) wired
      into puzzle lessons: drag-and-drop and click-to-move, legal-move
      highlighting, board orientation from FEN turn. The board only
      validates legality client-side — the resulting SAN move is submitted
      to the existing `/puzzles/{id}/attempt` endpoint, which remains the
      sole source of truth for correctness (puzzle answers were already
      stored as SAN, so no backend change was needed there).

## Set 8 (this update)
- [x] **3-Year Structured Training Plan migrated** (decision made: yes, on
      user request — previously confirmed missing from Sets 1-7). Migrated
      V16's `studyPlan.js` (threeYearPlan: 36 months across year1/year2/
      year3, each with weekly goals + 4 daily sessions + resources, plus
      the dailyPlans/weeklySchedules templates) as static JSON content
      served from `GET /training-plan`. Added a `TrainingPlanProgress`
      table (one row per user/item checked off) instead of V16's
      single-blob `Progress.done` JSON column, matching how this codebase
      already tracks puzzle/quiz attempts as real rows rather than blobs.
      New endpoints: `GET/PUT/DELETE /training-plan/progress[/{item_key}]`,
      `GET /training-plan/stats` (per-year completion %). New frontend
      route `/training-plan` (`TrainingPlanPage`), linked from the header
      and dashboard.
- [x] **Syllabus tracks migrated**. Migrated V16's `syllabusData.js`
      (5 curriculum-overview tracks incl. Junior Prodigy, the 3-Year Club
      Player Mastery pathway, and 3 "coming soon" tracks) as static JSON
      served from `GET /syllabus-tracks`. Kept deliberately separate from
      the DB-backed `Track`/`Course` model — these are descriptive
      marketing/curriculum content, not enrollable records. Dropped V16's
      `actionLink.page` field (old single-page-app navigation target with
      no router-path equivalent here); the new page links out to
      `/dashboard` generically instead. New frontend route `/syllabus`
      (`SyllabusPage`).

### Verified locally (Set 8)
- `alembic upgrade head` runs clean end-to-end on a fresh DB through the
  new `20260904_add_training_plan` migration.
- Booted the real FastAPI app and hit it with live requests: registered a
  user, logged in, marked/unmarked training-plan items, confirmed
  `/training-plan/stats` percentages update correctly, confirmed invalid
  item keys are rejected (400) and the progress routes require auth (401).
- `npm run build` succeeds with zero new ESLint warnings (the sole warning
  is the pre-existing, already-documented `chess.js` source-map issue —
  see `SOURCE_MAP_FIX.md`).

### Still open (carried over from Set 7)
- [ ] Rich master-game replay using a real chess rules library (current
      `GameViewer` just steps through a whitespace-split move-token string).
- [ ] Parent/coach notifications and assignments.
- [ ] Course recommendation tuning by age, level, and puzzle performance.
- [ ] Expanded automated API integration test coverage.
