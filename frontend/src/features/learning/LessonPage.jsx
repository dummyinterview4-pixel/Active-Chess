import {useEffect,useState} from 'react';
import {Link,useNavigate,useParams} from 'react-router-dom';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import PuzzleLesson from '../puzzles/PuzzleLesson';
import QuizLesson from '../quizzes/QuizLesson';
import {getLesson,completeLesson,getLessons} from '../../services/learningService';

export default function LessonPage(){
 const {lessonId}=useParams(); const nav=useNavigate();
 const [lesson,setLesson]=useState(null),[siblings,setSiblings]=useState([]),[done,setDone]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState('');
 useEffect(()=>{
  setLesson(null);setDone(false);setError('');
  getLesson(lessonId).then(async r=>{
    setLesson(r.data);
    try { const rows=await getLessons(r.data.chapter_id); setSiblings(rows.data||[]); } catch {}
  }).catch(e=>setError(e.response?.data?.detail||'Lesson not found.'));
 },[lessonId]);
 const finish=async()=>{
  setBusy(true);setError('');
  try{await completeLesson(Number(lessonId));setDone(true)}
  catch(e){setError(e.response?.data?.detail||'Please enroll before completing this lesson.')}
  finally{setBusy(false)}
 };
 if(!lesson)return <main className="kids-page"><Card><h2>{error||'Opening lesson… ♞'}</h2></Card></main>;
 const index=siblings.findIndex(x=>x.id===lesson.id), previous=index>0?siblings[index-1]:null, next=index>=0&&index<siblings.length-1?siblings[index+1]:null;
 return <main className="kids-page">
  <Link className="back-link" to={`/courses/${lesson.course_id}`}>← Back to lesson map</Link>
  <section className="lesson-shell"><Card>
   <span className="course-badge">LESSON {lesson.order+1} • {lesson.lesson_type}</span>
   <h1>{lesson.title}</h1><p className="lesson-description">{lesson.description}</p>
   <div className="lesson-content" dangerouslySetInnerHTML={{__html: lesson.content || '<p>Your coach is preparing this lesson.</p>'}} />
   {error&&<div className="error-box">😕 {error}</div>}
   {lesson.lesson_type==='puzzle'?<PuzzleLesson lessonId={lesson.id} onFinished={finish}/>
    :lesson.lesson_type==='quiz'?<QuizLesson lessonId={lesson.id} onFinished={finish}/>
    :null}
   {done?<div className="success-box">🎉 Great job! Lesson complete. ⭐</div>:(lesson.lesson_type!=='puzzle'&&lesson.lesson_type!=='quiz')&&<Button onClick={finish} disabled={busy}>{busy?'Saving your star…':'I finished this lesson ⭐'}</Button>}
   <div className="lesson-nav">
    {previous?<Button variant="secondary" onClick={()=>nav(`/lessons/${previous.id}`)}>← Previous</Button>:<span/>}
    {next?<Button onClick={()=>nav(`/lessons/${next.id}`)}>Next lesson →</Button>:done?<Button onClick={()=>nav('/')}>Adventure home 🏠</Button>:<span/>}
   </div>
  </Card></section>
 </main>
}
