import {useEffect,useState} from 'react';
import {Link,useParams} from 'react-router-dom';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import ProgressBar from '../../components/ui/ProgressBar';
import {getCourse,getChapters,getLessons,getCourseProgress,enroll} from '../../services/learningService';

export default function CoursePage(){
 const {courseId}=useParams(); const [course,setCourse]=useState(null); const [chapters,setChapters]=useState([]); const [lessons,setLessons]=useState({}); const [progress,setProgress]=useState(null); const [error,setError]=useState(''); const [busy,setBusy]=useState(false); const [couponCode,setCouponCode]=useState('FREE');
 const load=()=>Promise.all([getCourse(courseId),getChapters(courseId),getCourseProgress(courseId)]).then(async ([c,ch,p])=>{setCourse(c.data);setChapters(ch.data);setProgress(p.data); const rows=await Promise.all(ch.data.map(x=>getLessons(x.id))); setLessons(Object.fromEntries(ch.data.map((x,i)=>[x.id,rows[i].data])));}).catch(async e=>{ if(e.response?.status===403){ const c=await getCourse(courseId); setCourse(c.data); const ch=await getChapters(courseId); setChapters(ch.data); const rows=await Promise.all(ch.data.map(x=>getLessons(x.id))); setLessons(Object.fromEntries(ch.data.map((x,i)=>[x.id,rows[i].data]))); } else setError(e.response?.data?.detail||'Could not load this adventure.');});
 // eslint-disable-next-line react-hooks/exhaustive-deps
 useEffect(()=>{load()},[courseId]);
 const isPaid=course?.fee>0;
 const join=async()=>{setBusy(true);setError('');try{await enroll(Number(courseId),isPaid?couponCode:undefined);await load()}catch(e){setError(e.response?.data?.detail||'Could not join the course.')}finally{setBusy(false)}};
 if(!course&&!error)return <main className="kids-page"><Card><h2>Opening your adventure… 🧭</h2></Card></main>;
 return <main className="kids-page"><Link className="back-link" to="/">← Back to my adventure</Link>{error&&<div className="error-box">😕 {error}</div>}
 <section className="course-hero"><div><span className="course-badge">♟️ CHESS ADVENTURE</span><h1>{course?.name}</h1><p>{course?.description}</p>{progress&&<><div className="progress-caption"><b>{progress.percent}% complete</b><span>{progress.completed_lessons}/{progress.total_lessons} lessons</span></div><ProgressBar value={progress.percent}/></>}</div><div className="course-trophy">🏆</div></section>
 {!progress&&<Card className="join-card"><div><h2>Ready to start? 🚀</h2><p>{isPaid?'This course needs a coupon code for free access while payment isn\'t live yet.':'Join this course and unlock your lesson path.'}</p>{isPaid&&<input className="kids-input coupon-input" value={couponCode} onChange={e=>setCouponCode(e.target.value)} placeholder="Coupon code" />}</div><Button onClick={join} disabled={busy}>{busy?'Joining…':'Start this adventure →'}</Button></Card>}
 <h2>Your lesson map 🗺️</h2>{chapters.map((ch,i)=><Card key={ch.id} className="chapter-card"><div className="chapter-number">{i+1}</div><div className="chapter-body"><div><h3>{ch.title}</h3><p>{ch.description}</p></div><div className="lesson-list">{(lessons[ch.id]||[]).map((l,j)=><Link className="lesson-row" key={l.id} to={`/lessons/${l.id}`}><span className="lesson-icon">{j===0?'🌱':'⭐'}</span><span><b>{l.title}</b><small>{l.description||'A fun chess lesson'}</small></span><span>→</span></Link>)}</div></div></Card>)}</main>
}
