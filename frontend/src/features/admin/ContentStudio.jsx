import {useEffect,useState} from 'react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import {
 getAdminLessons,
 getAdminPuzzles,createAdminPuzzle,updateAdminPuzzle,deleteAdminPuzzle,
 getAdminQuizzes,createAdminQuiz,updateAdminQuiz,deleteAdminQuiz,
} from '../../services/learningService';

const EMPTY_PUZZLE={fen:'',prompt:'',answer:'',explanation:'',points:10};
const EMPTY_QUIZ={prompt:'',option_a:'',option_b:'',option_c:'',option_d:'',correct_option:'a',explanation:'',points:10};

export default function ContentStudio(){
 const [kind,setKind]=useState('puzzle');
 const [lessons,setLessons]=useState([]),[lessonId,setLessonId]=useState('');
 const [items,setItems]=useState([]),[editingId,setEditingId]=useState(null);
 const [form,setForm]=useState(EMPTY_PUZZLE);
 const [error,setError]=useState(''),[message,setMessage]=useState(''),[busy,setBusy]=useState(false);

 useEffect(()=>{getAdminLessons().then(r=>{setLessons(r.data);if(r.data.length&&!lessonId)setLessonId(String(r.data[0].id))}).catch(e=>setError(e.response?.data?.detail||'Could not load lessons.'))},[]); // eslint-disable-line react-hooks/exhaustive-deps

 const loadItems=async()=>{
  if(!lessonId)return;
  try{
   const r=kind==='puzzle'?await getAdminPuzzles(lessonId):await getAdminQuizzes(lessonId);
   setItems(r.data);
  }catch(e){setError(e.response?.data?.detail||'Could not load content.')}
 };
 useEffect(()=>{setForm(kind==='puzzle'?EMPTY_PUZZLE:EMPTY_QUIZ);setEditingId(null);loadItems()},[kind,lessonId]); // eslint-disable-line react-hooks/exhaustive-deps

 const startEdit=(item)=>{
  setEditingId(item.id);
  setForm(kind==='puzzle'
   ?{fen:item.fen,prompt:item.prompt,answer:item.answer,explanation:item.explanation||'',points:item.points}
   :{prompt:item.prompt,option_a:item.option_a,option_b:item.option_b,option_c:item.option_c,option_d:item.option_d,correct_option:item.correct_option,explanation:item.explanation||'',points:item.points});
 };
 const resetForm=()=>{setEditingId(null);setForm(kind==='puzzle'?EMPTY_PUZZLE:EMPTY_QUIZ)};

 const submit=async(e)=>{
  e.preventDefault();
  setBusy(true);setError('');setMessage('');
  try{
   const payload={...form,points:Number(form.points)||10};
   if(editingId){
    if(kind==='puzzle')await updateAdminPuzzle(editingId,payload);
    else await updateAdminQuiz(editingId,payload);
    setMessage('Updated! ⭐');
   }else{
    if(kind==='puzzle')await createAdminPuzzle({...payload,lesson_id:Number(lessonId)});
    else await createAdminQuiz({...payload,lesson_id:Number(lessonId)});
    setMessage('Added to the lesson! 🎉');
   }
   resetForm();
   await loadItems();
  }catch(e){setError(e.response?.data?.detail||'Could not save this item.')}
  finally{setBusy(false)}
 };

 const remove=async(id)=>{
  setBusy(true);setError('');setMessage('');
  try{
   if(kind==='puzzle')await deleteAdminPuzzle(id); else await deleteAdminQuiz(id);
   if(editingId===id)resetForm();
   await loadItems();
  }catch(e){setError(e.response?.data?.detail||'Could not delete this item.')}
  finally{setBusy(false)}
 };

 const toggleActive=async(item)=>{
  setBusy(true);setError('');
  try{
   if(kind==='puzzle')await updateAdminPuzzle(item.id,{is_active:!item.is_active});
   else await updateAdminQuiz(item.id,{is_active:!item.is_active});
   await loadItems();
  }catch(e){setError(e.response?.data?.detail||'Could not update this item.')}
  finally{setBusy(false)}
 };

 return <Card>
  <h2>Puzzle & Quiz Studio 🧩</h2>
  <p>Add chess puzzles and quiz questions to any lesson.</p>
  <div className="studio-tabs">
   <button type="button" className={`kids-btn ${kind==='puzzle'?'':'secondary'}`} onClick={()=>setKind('puzzle')}>Puzzles ♟️</button>
   <button type="button" className={`kids-btn ${kind==='quiz'?'':'secondary'}`} onClick={()=>setKind('quiz')}>Quizzes 🧠</button>
  </div>
  <label>Lesson
   <select className="kids-input" value={lessonId} onChange={e=>setLessonId(e.target.value)}>
    {lessons.map(l=><option key={l.id} value={l.id}>{l.course_name} → {l.chapter_title} → {l.title} ({l.lesson_type})</option>)}
   </select>
  </label>
  {error&&<div className="error-box">😕 {error}</div>}
  {message&&<div className="success-box">{message}</div>}

  <h3>{editingId?'Edit':'New'} {kind==='puzzle'?'puzzle':'quiz question'}</h3>
  <form onSubmit={submit} className="studio-form">
   {kind==='puzzle'?<>
    <label>FEN / position <input className="kids-input" value={form.fen} onChange={e=>setForm({...form,fen:e.target.value})} required /></label>
    <label>Prompt <input className="kids-input" value={form.prompt} onChange={e=>setForm({...form,prompt:e.target.value})} required /></label>
    <label>Correct answer (move) <input className="kids-input" value={form.answer} onChange={e=>setForm({...form,answer:e.target.value})} required /></label>
   </>:<>
    <label>Question <input className="kids-input" value={form.prompt} onChange={e=>setForm({...form,prompt:e.target.value})} required /></label>
    <label>Option A <input className="kids-input" value={form.option_a} onChange={e=>setForm({...form,option_a:e.target.value})} required /></label>
    <label>Option B <input className="kids-input" value={form.option_b} onChange={e=>setForm({...form,option_b:e.target.value})} required /></label>
    <label>Option C <input className="kids-input" value={form.option_c} onChange={e=>setForm({...form,option_c:e.target.value})} required /></label>
    <label>Option D <input className="kids-input" value={form.option_d} onChange={e=>setForm({...form,option_d:e.target.value})} required /></label>
    <label>Correct option
     <select className="kids-input" value={form.correct_option} onChange={e=>setForm({...form,correct_option:e.target.value})}>
      <option value="a">A</option><option value="b">B</option><option value="c">C</option><option value="d">D</option>
     </select>
    </label>
   </>}
   <label>Explanation (shown after answering) <input className="kids-input" value={form.explanation} onChange={e=>setForm({...form,explanation:e.target.value})} /></label>
   <label>Points <input className="kids-input" type="number" min="1" value={form.points} onChange={e=>setForm({...form,points:e.target.value})} /></label>
   <div className="admin-actions">
    <Button type="submit" disabled={busy||!lessonId}>{editingId?'Save changes':'Add to lesson'}</Button>
    {editingId&&<Button type="button" variant="secondary" onClick={resetForm}>Cancel edit</Button>}
   </div>
  </form>

  <h3>Existing {kind==='puzzle'?'puzzles':'quiz questions'}</h3>
  {!items.length&&<p>Nothing here yet — add the first one above! 🌱</p>}
  <div className="course-grid">{items.map(item=>
   <Card key={item.id}>
    <h4>{item.prompt}</h4>
    {kind==='puzzle'?<p><b>Answer:</b> {item.answer}</p>:<p><b>Correct:</b> {item.correct_option.toUpperCase()}</p>}
    <span className="age-pill">{item.is_active?'Active':'Hidden'} • {item.points} pts</span>
    <div className="admin-actions">
     <Button onClick={()=>startEdit(item)}>Edit</Button>
     <Button variant="secondary" onClick={()=>toggleActive(item)}>{item.is_active?'Hide':'Show'}</Button>
     <Button variant="secondary" onClick={()=>remove(item.id)}>Delete</Button>
    </div>
   </Card>
  )}</div>
 </Card>
}
