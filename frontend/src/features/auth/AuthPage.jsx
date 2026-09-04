import {useEffect,useState} from 'react';
import {Link,useLocation,useNavigate} from 'react-router-dom';
import {useAuth} from '../../store/AuthContext';
import Button from '../../components/ui/Button';

export default function AuthPage(){
 const {login,register,user}=useAuth(); const nav=useNavigate(); const location=useLocation();
 const [mode,setMode]=useState(location.pathname==='/register'?'register':'login');
 const [form,setForm]=useState({username:'',email:'',full_name:'',password:'',role:'student'}),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 useEffect(()=>{if(user) nav('/dashboard',{replace:true})},[user,nav]);
 const switchMode=m=>{setMode(m);setError('');nav(m==='register'?'/register':'/login',{replace:true})};
 const submit=async e=>{e.preventDefault();setBusy(true);setError('');try{if(mode==='login')await login(form.username,form.password);else await register(form);}catch(err){setError(err.response?.data?.detail||err.message||'Something went wrong.');}finally{setBusy(false)}};
 return <main className="auth-wrap">
  <section className="auth-hero"><Link className="auth-home-link" to="/">← Back to Active-Chess</Link><div className="big-knight">♞</div><h1>Chess can be an <span>adventure!</span> 🚀</h1><p>Learn one fun idea at a time, practise your skills, earn stars and become a stronger player.</p><div className="floating-pieces">♟️ ♞ ♗ ♜ ♕</div></section>
  <section className="auth-card"><div className="tab-row"><button type="button" className={mode==='login'?'selected':''} onClick={()=>switchMode('login')}>I’m back 👋</button><button type="button" className={mode==='register'?'selected':''} onClick={()=>switchMode('register')}>New player 🌟</button></div>
   <div className="auth-intro"><h2>{mode==='login'?'Welcome back!':'Start your chess journey'}</h2><p>{mode==='login'?'Sign in to continue where you left off.':'Create your account and discover your learning path.'}</p></div>
   <form onSubmit={submit}>{mode==='register'&&<><label>Account type<select className="kids-input" value={form.role} onChange={e=>setForm({...form,role:e.target.value})}><option value="student">Student</option><option value="parent">Parent / guardian</option></select></label><label>Your name<input value={form.full_name} onChange={e=>setForm({...form,full_name:e.target.value})}/></label><label>Email<input type="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} required/></label></>}
    <label>Username<input value={form.username} onChange={e=>setForm({...form,username:e.target.value})} required autoComplete="username"/></label><label>Password<input type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} required minLength="6" autoComplete={mode==='login'?'current-password':'new-password'}/></label>
    {error&&<div className="error-box">😕 {error}</div>}<Button disabled={busy}>{busy?'One moment…':mode==='login'?'Let’s Play ♟️':'Start My Adventure 🚀'}</Button>
   </form><p className="auth-bottom">{mode==='login'?<>New here? <button type="button" onClick={()=>switchMode('register')}>Create an account</button></>:<>Already registered? <button type="button" onClick={()=>switchMode('login')}>Sign in</button></>}</p>
  </section>
 </main>
}
