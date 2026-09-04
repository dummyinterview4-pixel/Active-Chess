import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../store/AuthContext';
import Card from '../../components/ui/Card';
import ProgressBar from '../../components/ui/ProgressBar';
import {
  getTrainingPlan, getTrainingPlanProgress, getTrainingPlanStats,
  markTrainingPlanItem, unmarkTrainingPlanItem,
} from '../../services/learningService';

const YEAR_LABEL = { year1: 'Year 1', year2: 'Year 2', year3: 'Year 3' };

export default function TrainingPlanPage() {
  const { user } = useAuth();
  const [plan, setPlan] = useState(null);
  const [done, setDone] = useState({}); // item_key -> true
  const [stats, setStats] = useState([]);
  const [error, setError] = useState('');
  const [yearKey, setYearKey] = useState('year1');
  const [month, setMonth] = useState(1);
  const [saving, setSaving] = useState({});

  useEffect(() => {
    getTrainingPlan().then(r => setPlan(r.data)).catch(() => setError('Could not load the training plan. Please refresh and try again.'));
  }, []);

  useEffect(() => {
    if (!user) return;
    getTrainingPlanProgress().then(r => {
      const map = {};
      (r.data.completed_items || []).forEach(k => { map[k] = true; });
      setDone(map);
    }).catch(() => {});
    getTrainingPlanStats().then(r => setStats(r.data)).catch(() => {});
  }, [user]);

  const months = useMemo(() => plan ? plan.threeYearPlan[yearKey].months : [], [plan, yearKey]);
  const m = useMemo(() => months.find(x => x.month === month) || months[0], [months, month]);
  const yearStats = stats.find(s => s.year === yearKey);

  if (error) return <main className="kids-page"><Card><h3>😕 {error}</h3></Card></main>;
  if (!plan || !m) return <div className="loading-screen">♞<span>Loading the training plan…</span></div>;

  const sessions = Object.entries(m.dailyPlan || {});
  const goalsDone = m.weeklyGoals.filter((_, i) => done[`m${m.month}-g${i}`]).length;
  const sessionsDone = sessions.filter(([k]) => done[`m${m.month}-${k}`]).length;
  const totalItems = m.weeklyGoals.length + sessions.length;
  const monthPct = totalItems ? Math.round(((goalsDone + sessionsDone) / totalItems) * 100) : 0;

  const toggle = async (key) => {
    if (!user) return;
    const isDone = !!done[key];
    setSaving(s => ({ ...s, [key]: true }));
    setDone(d => ({ ...d, [key]: !isDone }));
    try {
      if (isDone) await unmarkTrainingPlanItem(key); else await markTrainingPlanItem(key);
      getTrainingPlanStats().then(r => setStats(r.data)).catch(() => {});
    } catch {
      setDone(d => ({ ...d, [key]: isDone })); // revert on failure
    } finally {
      setSaving(s => ({ ...s, [key]: false }));
    }
  };

  return (
    <main className="kids-page narrow">
      <section className="welcome-card">
        <div>
          <span className="mini-label">{plan.threeYearPlan.subtitle}</span>
          <h1>{plan.threeYearPlan.title} 🗺️</h1>
          <p>Every month of your 36-month journey, with weekly goals and daily sessions you can check off as you go.</p>
        </div>
        <div className="mascot">♟️</div>
      </section>

      {!user && (
        <Card><p>👋 <Link to="/login">Sign in</Link> to save your checkmarks — you can still browse the whole plan without an account.</p></Card>
      )}

      <div className="cat-tabs" style={{ marginBottom: 14 }}>
        {['year1', 'year2', 'year3'].map(yk => (
          <button
            key={yk}
            className={yearKey === yk ? 'active' : ''}
            onClick={() => { setYearKey(yk); setMonth(plan.threeYearPlan[yk].months[0].month); }}
          >
            {YEAR_LABEL[yk]}: {plan.threeYearPlan[yk].title.replace(/^Year \d: /, '')}
            {stats.length > 0 && (
              <span className="view-toggle-pct">
                {(stats.find(s => s.year === yk) || {}).percent || 0}%
              </span>
            )}
          </button>
        ))}
      </div>

      {yearStats && <ProgressBar value={yearStats.percent} />}

      <div className="tut-nav">
        <select className="tut-nav-jump" value={m.month} onChange={e => setMonth(Number(e.target.value))}>
          {months.map(x => (
            <option key={x.month} value={x.month}>Month {x.month} — {x.title}</option>
          ))}
        </select>
      </div>

      <Card>
        <h2>Month {m.month}: {m.title}</h2>
        <p>{m.focus}</p>
        <ProgressBar value={monthPct} />
        <small className="course-progress-label">{monthPct}% of this month checked off</small>
      </Card>

      <h2>Weekly goals 🎯</h2>
      <Card>
        <ul className="checklist">
          {m.weeklyGoals.map((goal, i) => {
            const key = `m${m.month}-g${i}`;
            return (
              <li key={key}>
                <label className={`check-row ${done[key] ? 'checked' : ''}`}>
                  <input
                    type="checkbox"
                    checked={!!done[key]}
                    disabled={!user || saving[key]}
                    onChange={() => toggle(key)}
                  />
                  {goal}
                </label>
              </li>
            );
          })}
        </ul>
      </Card>

      <h2>Daily sessions 📅</h2>
      <div className="course-grid">
        {sessions.map(([k, s]) => {
          const key = `m${m.month}-${k}`;
          return (
            <Card key={key}>
              <label className={`check-row ${done[key] ? 'checked' : ''}`}>
                <input
                  type="checkbox"
                  checked={!!done[key]}
                  disabled={!user || saving[key]}
                  onChange={() => toggle(key)}
                />
                <b>{s.activity}</b> <small>({s.duration} min)</small>
              </label>
              <p>{s.details}</p>
            </Card>
          );
        })}
      </div>

      {m.resources && m.resources.length > 0 && (
        <Card className="quick-links">
          <h2>Recommended resources 📚</h2>
          <ul>
            {m.resources.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </Card>
      )}
    </main>
  );
}
