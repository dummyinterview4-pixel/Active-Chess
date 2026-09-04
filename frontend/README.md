# Active Chess - Frontend

## Tech Stack
- **Framework**: React 18
- **Routing**: React Router v6
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Chess Library**: chess.js & chessboard.js
- **State Management**: Zustand

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Navbar.js
│   │   ├── ChessBoard.js
│   │   ├── PuzzleCard.js
│   │   └── ProgressBar.js
│   ├── pages/
│   │   ├── Login.js
│   │   ├── Register.js
│   │   ├── Dashboard.js
│   │   ├── CourseDetail.js
│   │   ├── Tutorial.js
│   │   ├── PuzzleSolver.js
│   │   └── AdminPanel.js
│   ├── utils/
│   │   ├── api.js
│   │   └── auth.js
│   ├── App.js
│   └── index.js
├── package.json
└── README.md
```

## Features

✅ User Authentication (Login/Register)
✅ Course Dashboard with Coupon-based Enrollment
✅ Course Details & Progress Tracking
✅ Interactive Tutorial Player
✅ Chess Puzzle Solver (FEN notation support)
✅ Activity Logging
✅ Admin Panel for Course Management

## Setup Instructions

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm start
   ```

4. Build for production:
   ```bash
   npm run build
   ```

## Pages

### Authentication Pages
- **Login** - User login with username & password
- **Register** - New user registration

### User Pages
- **Dashboard** - View all available courses and enroll with coupon
- **CourseDetail** - View course content and tutorials
- **Tutorial** - Watch tutorial videos and practice puzzles
- **PuzzleSolver** - Interactive chess puzzle solver

### Admin Pages
- **AdminPanel** - Create and manage courses, view statistics

## Environment Variables

Create a `.env` file in the frontend directory:
```
REACT_APP_API_URL=http://localhost:8000
```

## Integration with Backend

The frontend connects to the FastAPI backend at `http://localhost:8000`:

- Authentication endpoints: `/auth/login`, `/auth/register`
- Courses endpoints: `/courses/`, `/courses/{id}`
- Enrollments endpoints: `/enrollments/`
- Tutorials endpoints: `/tutorials/` (to be added)
- Puzzles endpoints: `/puzzles/` (to be added)
- Progress endpoints: `/progress/` (to be added)

## Component Dependencies

### ChessBoard Component
Uses `chess.js` for game logic and `chessboard.js` for UI rendering.

### Puzzle Solver
- Displays puzzle in FEN notation
- Allows moves and validates against solution
- Tracks attempts and score
- Records activity/progress

## Future Enhancements

- [ ] Real-time multiplayer games
- [ ] Leaderboards
- [ ] Video streaming for tutorials
- [ ] Mobile responsive design improvements
- [ ] Dark/Light theme toggle
- [ ] Notifications system
- [ ] User profile page
- [ ] Progress analytics
