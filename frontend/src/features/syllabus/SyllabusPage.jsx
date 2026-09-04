import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Card from '../../components/ui/Card';
import { getSyllabusTracks } from '../../services/learningService';

export default function SyllabusPage() {
  const [tracks, setTracks] = useState([]);
  const [error, setError] = useState('');
  const [openId, setOpenId] = useState(null);

  useEffect(() => {
    getSyllabusTracks().then(r => setTracks(r.data)).catch(() => setError('Could not load the syllabus. Please refresh and try again.'));
  }, []);

  return (
    <main className="kids-page narrow">
      <section className="welcome-card">
        <div>
          <span className="mini-label">CURRICULUM & TRACKS</span>
          <h1>Find your path 🧭</h1>
          <p>Structured learning tracks for every kind of chess journey, from a kid's first game to a titled player's opening prep.</p>
        </div>
        <div className="mascot">🗺️</div>
      </section>

      {error && <div className="error-box">😕 {error}</div>}

      <div className="track-grid">
        {tracks.map(t => (
          <Card key={t.id} className="track-card">
            <div className="track-icon" style={{ backgroundColor: `${t.color}15`, color: t.color }}>{t.icon}</div>
            <div>
              <span className={`age-pill ${t.status === 'coming_soon' ? 'ghost-btn' : ''}`}>
                {t.status === 'coming_soon' ? 'Coming soon' : t.badge}
              </span>
              <h3>{t.title}</h3>
              <p>{t.subtitle}</p>
              <small className="course-progress-label">{t.level} · {t.duration} · {t.hours}</small>

              <button className="kids-btn secondary full" onClick={() => setOpenId(openId === t.id ? null : t.id)}>
                {openId === t.id ? 'Hide phases ▲' : 'See the phases ▼'}
              </button>

              {openId === t.id && (
                <ul className="checklist">
                  {t.phases.map((phase, i) => (
                    <li key={i}>
                      <b>{phase.name}</b>
                      <p>{phase.focus}</p>
                      {phase.outcomes && phase.outcomes.length > 0 && (
                        <ul>{phase.outcomes.map((o, j) => <li key={j}>{o}</li>)}</ul>
                      )}
                    </li>
                  ))}
                </ul>
              )}

              {t.status !== 'coming_soon' && (
                <Link className="kids-btn full" to="/dashboard">{t.ctaLabel || 'Explore courses →'}</Link>
              )}
            </div>
          </Card>
        ))}
      </div>

      {!tracks.length && !error && (
        <Card><h3>Loading tracks… 🧩</h3></Card>
      )}
    </main>
  );
}
