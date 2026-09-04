import {useEffect,useState} from 'react';
import api from '../../services/apiClient';
import PuzzleChessBoard from '../../components/chess/PuzzleChessBoard';

export default function PuzzleLesson({lessonId,onFinished}){
 const [puzzles,setPuzzles]=useState([]),[index,setIndex]=useState(0),[result,setResult]=useState(null),[score,setScore]=useState(0),[loading,setLoading]=useState(true),[newBadge,setNewBadge]=useState(null),[submitting,setSubmitting]=useState(false),[resetKey,setResetKey]=useState(0);
 useEffect(()=>{api.get(`/puzzles/lesson/${lessonId}`).then(r=>setPuzzles(r.data)).finally(()=>setLoading(false))},[lessonId]);
 const p=puzzles[index];
 const submitMove=async(san)=>{
  if(!p||submitting||result)return;
  setSubmitting(true);
  try{
   const r=await api.post(`/puzzles/${p.id}/attempt`,{answer:san});
   setResult(r.data);
   if(r.data.correct){
    setScore(s=>s+r.data.points);
    if(r.data.new_badges?.length)setNewBadge(r.data.new_badges[0]);
   }else{
    window.setTimeout(()=>{setResult(null);setResetKey(k=>k+1)},1100);
   }
  }finally{setSubmitting(false)}
 };
 const next=()=>{setResult(null);setNewBadge(null);if(index+1<puzzles.length)setIndex(i=>i+1);else onFinished?.()};
 if(loading)return <div className="puzzle-card">Loading your chess challenge… ♟️</div>;
 if(!puzzles.length)return <div className="puzzle-card"><h3>No puzzles yet 🌱</h3><p>Your coach can add challenges to this lesson.</p></div>;
 return <div className="puzzle-card">
   <div className="puzzle-progress">CHALLENGE {index+1} / {puzzles.length} ⭐</div>
   <h2>{p.prompt}</h2>
   <p className="puzzle-hint-text">Drag a piece — or click it, then click where it should go.</p>
   <PuzzleChessBoard key={p.id} fen={p.fen} locked={submitting||!!result} resetKey={resetKey} onMove={submitMove} />
   {result&&(
     <div className={result.correct?'success-box':'error-box'}>
       {result.correct?'🎉 Brilliant! That was the winning move.':'💡 Not quite — try again!'}
       {result.correct&&result.explanation&&<p>{result.explanation}</p>}
       {newBadge&&<p className="badge-toast">🏅 New badge: {newBadge}!</p>}
       {result.correct&&<button className="kids-btn" onClick={next}>{index+1<puzzles.length?'Next challenge →':'Finish puzzles ⭐'}</button>}
     </div>
   )}
   <div className="score-badge">Score: {score} ⭐</div>
 </div>
}
