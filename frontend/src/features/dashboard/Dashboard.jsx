import {useEffect,useState} from 'react';
import {useAuth} from '../../store/AuthContext';
import {Link} from 'react-router-dom';
import api from '../../services/apiClient';
import {getMyStats,getMyBadges} from '../../services/learningService';
import Card from '../../components/ui/Card';
import ProgressBar from '../../components/ui/ProgressBar';
import {getRecommendations} from '../../services/learningService';

export default function Dashboard(){
 const {user}=useAuth();
 const [tracks,setTracks]=useState([]),[courses,setCourses]=useState([]),[enrolled,setEnrolled]=useState([]),[courseProgress,setCourseProgress]=useState({}),[nextLesson,setNextLesson]=useState(null),[error,setError]=useState('');
 const [recommendations,setRecommendations]=useState([]),[stats,setStats]=useState({total_stars:0,current_streak:0,longest_streak:0}),[badges,setBadges]=useState([]);
 useEffect(()=>{
  Promise.allSettled([api.get('/tracks'),api.get('/courses'),api.get('/me/progress'),api.get('/me/enrollments'),api.get('/me/next-lesson')]).then(async results=>{
   const value=i=>results[i].status==='fulfilled'?results[i].value:null;
   const a=value(0),b=value(1),d=value(3),e=value(4);
   if(a)setTracks(a.data||[]); if(b)setCourses(b.data||[]); if(d)setEnrolled(d.data||[]); if(e)setNextLesson(e.data||null);
   if(!b||!d){setError('We could not load your course list. Please refresh and try again.');return;}
   const publishedIds=new Set((b.data||[]).map(c=>c.id));
   const activeEnrolments=(d.data||[]).filter(x=>x.status==='active'&&publishedIds.has(x.course_id));
   const rows=await Promise.allSettled(activeEnrolments.map(x=>api.get(`/courses/${x.course_id}/progress`)));
   const progress={}; activeEnrolments.forEach((x,i)=>{if(rows[i].status==='fulfilled')progress[x.course_id]=rows[i].value.data}); setCourseProgress(progress);
  }).catch(()=>setError('Could not load your chess adventure. Please refresh and try again.'));
  getRecommendations().then(r=>setRecommendations(r.data)).catch(()=>{});
  getMyStats().then(r=>setStats(r.data)).catch(()=>{});
  getMyBadges().then(r=>setBadges(r.data)).catch(()=>{});
 },[]);
 const isEnrolled=id=>enrolled.some(e=>e.course_id===id&&e.status==='active');
 return <main className="kids-page">
  <section className="welcome-card"><div><span className="mini-label">TODAY’S CHESS MISSION</span><h1>Let’s make a <span>great move!</span> 🌟</h1><p>Pick a path below and keep collecting your chess stars.</p></div><div className="mascot">♞</div></section>
  <section className="stats-row"><Card><b>⭐ {stats.total_stars}</b><small>Stars earned</small></Card><Card><b>🔥 {stats.current_streak}</b><small>Day streak</small></Card><Card><b>🏆 {badges.length}</b><small>Badges earned</small></Card></section>
  {error&&<div className="error-box">😕 {error}</div>}
  {nextLesson&&<Card className="next-mission"><div><span className="mini-label">YOUR NEXT MISSION</span><h2>{nextLesson.title} ⭐</h2><p>Ready for one more fun chess step?</p></div><Link className="kids-btn mission-btn" to={`/lessons/${nextLesson.lesson_id}`}>Continue →</Link></Card>}
  {badges.length>0&&<section className="badge-shelf"><h2>Your badges 🎖️</h2><div className="badge-row">{badges.map(b=><div key={b.badge.code} className="badge-pill" title={b.badge.description}><span>{b.badge.icon}</span>{b.badge.name}</div>)}</div></section>}
  {recommendations.length>0&&<section><h2>Recommended next ⭐</h2><div className="course-grid">{recommendations.map(r=><Card key={r.course_id}><h3>{r.course_name}</h3><p>{r.reason}</p><Link className="kids-btn full" to={`/courses/${r.course_id}`}>Explore course →</Link></Card>)}</div></section>}
  <h2>Choose your adventure 🗺️</h2><div className="track-grid">{tracks.map(t=><Card key={t.id} className="track-card"><div className="track-icon">{t.icon}</div><div><h3>{t.name}</h3><p>{t.description||'A fun path to become a stronger chess player.'}</p><span className="age-pill">Ages {t.age_min||5}–{t.age_max||18}</span></div></Card>)}</div>
  <h2>Your courses 📚</h2><div className="course-grid">{courses.map(c=>{const cp=courseProgress[c.id];return <Card key={c.id}><span className="course-badge">{c.duration_months} MONTHS</span><h3>{c.name}</h3><p>{c.description}</p><ProgressBar value={cp?.percent||0}/><small className="course-progress-label">{cp?`${cp.completed_lessons}/${cp.total_lessons} lessons complete`:'Not started yet'}</small><Link className="kids-btn full" to={`/courses/${c.id}`}>{isEnrolled(c.id)?'Continue Course →':'Start Course →'}</Link></Card>})}</div>
  <Card className="quick-links"><h2>More chess adventures ♟️</h2><div className="quick-link-row"><Link className="kids-btn secondary" to="/training-plan">3-Year Plan 🗺️</Link><Link className="kids-btn secondary" to="/syllabus">Syllabus 🧭</Link><Link className="kids-btn secondary" to="/master-games">Master games 🎓</Link>{['coach','trainer','admin'].includes(user?.role)&&<Link className="kids-btn secondary" to="/coach">Coach dashboard 🧑‍🏫</Link>}{user?.role==='parent'&&<Link className="kids-btn secondary" to="/parent">Parent dashboard 👨‍👩‍👧</Link>}</div></Card>
  {!tracks.length&&!courses.length&&!error&&<Card><h3>Your adventure is being prepared! 🧩</h3><p>Your coach will add the first course soon.</p></Card>}
 </main>
}
