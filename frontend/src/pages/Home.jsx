import {Link} from 'react-router-dom';
import {useAuth} from '../store/AuthContext';
import Card from '../components/ui/Card';

const features = [
  ['🗺️', 'Structured learning paths', 'Follow a clear journey from chess fundamentals to tactics, strategy, calculation and practical play.'],
  ['♟️', 'Interactive practice', 'Learn through lessons, puzzles and quizzes instead of only reading chess theory.'],
  ['⭐', 'Progress that motivates', 'Earn stars, build streaks and collect badges as you complete meaningful learning activities.'],
  ['🎓', 'Learn from master games', 'Study selected games and connect real chess ideas with what you learn in your lessons.'],
  ['👨‍👩‍👧', 'Built for families and coaches', 'Parents can follow student progress and coaches can manage learning content and students.'],
  ['🚀', 'Learn at your pace', 'Return anytime, continue from your next lesson and build your chess skills step by step.'],
];

export default function Home(){
  const {user}=useAuth();
  return <main className="home-page">
    <section className="home-hero">
      <div className="home-hero-copy">
        <span className="eyebrow">♞ ACTIVE-CHESS</span>
        <h1>Turn chess practice into an <span>adventure.</span></h1>
        <p className="home-lead">Active-Chess is a friendly chess learning portal where students learn the right ideas, practise them, track their progress and keep improving one move at a time.</p>
        <div className="home-actions">
          <Link className="kids-btn" to={user?'/dashboard':'/login'}>{user?'Continue learning →':'Start learning free →'}</Link>
          {!user&&<Link className="home-secondary" to="/login">I already have an account</Link>}
        </div>
        <div className="home-trust"><span>♟️ Lessons</span><span>⭐ Stars</span><span>🔥 Streaks</span><span>🏅 Badges</span></div>
      </div>
      <div className="home-board" aria-hidden="true"><div className="home-board-glow">♞</div><div className="board-mini">♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜<br/>♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟<br/>· · · · · · · ·<br/>· · · ♟ · · ·<br/>· · · · · · ·<br/>· · · · · · ·<br/>♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙<br/>♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖</div></div>
    </section>

    <section className="home-section intro-section">
      <div className="section-heading"><span className="mini-label">WHY ACTIVE-CHESS?</span><h2>More than a place to play chess</h2><p>Chess improvement is easier when every lesson has a purpose and every practice session moves you forward.</p></div>
      <div className="feature-grid">{features.map(([icon,title,text])=><Card key={title} className="home-feature"><div className="feature-icon">{icon}</div><h3>{title}</h3><p>{text}</p></Card>)}</div>
    </section>

    <section className="home-section how-section">
      <div className="section-heading"><span className="mini-label">HOW IT WORKS</span><h2>Your chess journey is simple</h2></div>
      <div className="journey-grid"><div><b>01</b><h3>Choose your path</h3><p>Find a course that matches your level and goals.</p></div><div><b>02</b><h3>Learn the idea</h3><p>Work through focused lessons with clear explanations.</p></div><div><b>03</b><h3>Practise</h3><p>Use puzzles and quizzes to turn knowledge into skill.</p></div><div><b>04</b><h3>Keep improving</h3><p>Track progress, earn rewards and continue to the next lesson.</p></div></div>
    </section>

    <section className="home-cta"><div><span className="mini-label">READY WHEN YOU ARE</span><h2>Your next great move starts here.</h2><p>You do not need to be an expert. Start where you are and let Active-Chess guide the journey.</p></div><Link className="kids-btn" to={user?'/dashboard':'/login'}>{user?'Go to my dashboard':'Create your account →'}</Link></section>
  </main>
}
