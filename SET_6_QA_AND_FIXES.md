# Active-Chess — Stabilization, UX & Authentication Fixes

## User-facing issues fixed
- Public `/` is now a real Active-Chess home page instead of redirecting visitors to login.
- Added a clear explanation of what Active-Chess is, why to join, features, learning journey, and calls to action.
- Added public Sign in / Join navigation in the header.
- Added a real `/register` route; the previous register tab could navigate to an unregistered route.
- Successful login and registration now navigate automatically to `/dashboard`.
- Auth failures clear stale tokens so the application does not get stuck with an invalid session.
- Authenticated users visiting `/login` or `/register` are redirected to their dashboard.
- Dashboard is now a dedicated protected route at `/dashboard`.
- Dashboard data loading is resilient: one non-critical API failure no longer blanks the entire dashboard.
- Fixed duplicate React imports/routes left in the Set 6 App component.
- Brand navigation now correctly points to the public home page when logged out and dashboard when logged in.

## Verification
- Backend tests: `2 passed`.
- Backend Python compilation: passed.
- Frontend dependency/build verification remains environment-limited because npm dependency resolution timed out in this execution environment.
