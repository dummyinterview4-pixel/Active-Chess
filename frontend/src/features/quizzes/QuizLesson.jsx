import {useEffect,useState} from 'react';
import {getQuizzes,attemptQuiz} from '../../services/learningService';

export default function QuizLesson({lessonId,onFinished}){
 const [questions,setQuestions]=useState([]),[index,setIndex]=useState(0),[selected,setSelected]=useState(''),[result,setResult]=useState(null),[score,setScore]=useState(0),[loading,setLoading]=useState(true),[newBadge,setNewBadge]=useState(null);
 useEffect(()=>{getQuizzes(lessonId).then(r=>setQuestions(r.data)).finally(()=>setLoading(false))},[lessonId]);
 const submit=async()=>{if(!selected||!questions[index])return;const r=await attemptQuiz(questions[index].id,selected);setResult(r.data);if(r.data.correct)setScore(s=>s+r.data.points);if(r.data.new_badges?.length)setNewBadge(r.data.new_badges[0])};
 const next=()=>{setResult(null);setSelected('');setNewBadge(null);if(index+1<questions.length)setIndex(i=>i+1);else onFinished?.()};
 if(loading)return <div className="puzzle-card">Loading your quiz… 🧠</div>;
 if(!questions.length)return <div className="puzzle-card"><h3>No quiz yet 🌱</h3><p>Your coach can add quiz questions to this lesson.</p></div>;
 const q=questions[index];
 const options=[['a',q.option_a],['b',q.option_b],['c',q.option_c],['d',q.option_d]];
 return <div className="puzzle-card">
   <div className="puzzle-progress">QUESTION {index+1} / {questions.length} 🧠</div>
   <h2>{q.prompt}</h2>
   <div className="quiz-options">{options.map(([letter,text])=>(
     <button key={letter} type="button" className={`quiz-option${selected===letter?' selected':''}`} disabled={!!result} onClick={()=>setSelected(letter)}>
       <span className="quiz-letter">{letter.toUpperCase()}</span>{text}
     </button>
   ))}</div>
   {!result?<button className="kids-btn" onClick={submit} disabled={!selected}>Check my answer 🔎</button>:
     <div className={result.correct?'success-box':'error-box'}>
       {result.correct?'🎉 Brilliant!':'💡 Not quite — keep learning!'} {result.explanation&&<p>{result.explanation}</p>}
       {newBadge&&<p className="badge-toast">🏅 New badge: {newBadge}!</p>}
       <button className="kids-btn" onClick={next}>{index+1<questions.length?'Next question →':'Finish quiz ⭐'}</button>
     </div>}
   <div className="score-badge">Score: {score} ⭐</div>
 </div>
}
