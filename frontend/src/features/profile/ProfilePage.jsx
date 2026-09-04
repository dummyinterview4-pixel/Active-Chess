import {useEffect,useState} from 'react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import {getMyProfile,updateMyProfile} from '../../services/learningService';

const AVATARS=['🦁','🐯','🐼','🦊','🐸','🐵','🦄','🐲','🐧','🐢','🦉','🐬'];

export default function ProfilePage(){
 const [displayName,setDisplayName]=useState(''),[avatar,setAvatar]=useState(AVATARS[0]),[age,setAge]=useState(''),[loading,setLoading]=useState(true),[saving,setSaving]=useState(false),[saved,setSaved]=useState(false),[error,setError]=useState('');
 useEffect(()=>{
  getMyProfile().then(r=>{
   setDisplayName(r.data.display_name||'');
   setAvatar(r.data.avatar||AVATARS[0]);
   setAge(r.data.age??'');
  }).catch(e=>setError(e.response?.data?.detail||'Could not load your profile.')).finally(()=>setLoading(false));
 },[]);
 const save=async()=>{
  setSaving(true);setError('');setSaved(false);
  try{
   await updateMyProfile({display_name:displayName||null,avatar,age:age===''?null:Number(age)});
   setSaved(true);
  }catch(e){setError(e.response?.data?.detail||'Could not save your profile.')}
  finally{setSaving(false)}
 };
 if(loading)return <main className="kids-page"><Card><h2>Loading your profile… 🧸</h2></Card></main>;
 return <main className="kids-page">
  <section className="welcome-card"><div><span className="mini-label">MY PROFILE</span><h1>Make it <span>yours!</span> 🎨</h1><p>Pick your avatar and tell us your name.</p></div><div className="mascot">{avatar}</div></section>
  <Card>
   <h2>Choose your avatar</h2>
   <div className="avatar-grid">{AVATARS.map(a=>
     <button key={a} type="button" className={`avatar-choice${avatar===a?' selected':''}`} onClick={()=>setAvatar(a)} aria-label={`Choose avatar ${a}`}>{a}</button>
   )}</div>
   <h2>Your name</h2>
   <input className="kids-input" value={displayName} onChange={e=>setDisplayName(e.target.value)} placeholder="What should we call you?" maxLength={40} />
   <h2>Your age</h2>
   <input className="kids-input" type="number" min="3" max="18" value={age} onChange={e=>setAge(e.target.value)} placeholder="How old are you?" />
   {error&&<div className="error-box">😕 {error}</div>}
   {saved&&<div className="success-box">🎉 Saved! Looking great.</div>}
   <Button onClick={save} disabled={saving}>{saving?'Saving…':'Save my profile ⭐'}</Button>
  </Card>
 </main>
}
