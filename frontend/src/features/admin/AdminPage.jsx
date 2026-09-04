import {useEffect,useState} from 'react';
import api from '../../services/apiClient';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button'; import {useAuth} from '../../store/AuthContext';
import ContentStudio from './ContentStudio';
import {getAdminCoupons,createAdminCoupon,updateAdminCoupon} from '../../services/learningService';

export default function AdminPage(){
 const {user}=useAuth();
 const [tracks,setTracks]=useState([]),[courses,setCourses]=useState([]),[error,setError]=useState(''),[message,setMessage]=useState('');
 const [coupons,setCoupons]=useState([]),[newCode,setNewCode]=useState(''),[newMax,setNewMax]=useState(''),[couponBusy,setCouponBusy]=useState(false);
 const load=async()=>{try{const [t,c,cp]=await Promise.all([api.get('/tracks'),api.get('/courses'),getAdminCoupons()]);setTracks(t.data);setCourses(c.data);setCoupons(cp.data)}catch(e){setError(e.response?.data?.detail||'Could not load content studio.')}};
 useEffect(()=>{if(user?.role==='admin')load()},[user]);
 if(user?.role!=='admin') return <main className="kids-page"><Card><h2>Coach area only 🛡️</h2><p>This page is for coaches and admins.</p></Card></main>;
 const publish=async(type,id)=>{
  setMessage('');setError('');
  try{await api.patch(`/admin/${type}/${id}/publish`);setMessage('Updated publishing status ⭐');load()}
  catch(e){setError(e.response?.data?.detail||'Could not update publishing status.')}
 };
 const createCoupon=async(e)=>{
  e.preventDefault();setCouponBusy(true);setMessage('');setError('');
  try{
   await createAdminCoupon({code:newCode,max_redemptions:newMax?Number(newMax):null});
   setNewCode('');setNewMax('');setMessage('Coupon created 🎟️');load();
  }catch(e){setError(e.response?.data?.detail||'Could not create that coupon.')}
  finally{setCouponBusy(false)}
 };
 const toggleCoupon=async(coupon)=>{
  setMessage('');setError('');
  try{await updateAdminCoupon(coupon.id,{is_active:!coupon.is_active});setMessage('Updated coupon status 🎟️');load()}
  catch(e){setError(e.response?.data?.detail||'Could not update that coupon.')}
 };
 return <main className="kids-page">
  <section className="welcome-card"><div><span className="mini-label">COACH CONTENT STUDIO</span><h1>Build the chess adventure 🧩</h1><p>Prepare tracks and courses, then publish them when they are ready for kids.</p></div><div className="mascot">🧑‍🏫</div></section>
  {error&&<div className="error-box">😕 {error}</div>}{message&&<div className="success-box">🎉 {message}</div>}
  <h2>Tracks 🗺️</h2><div className="course-grid">{tracks.map(t=><Card key={t.id}><h3>{t.icon} {t.name}</h3><p>{t.description}</p><span className="age-pill">{t.is_active?'Visible to kids':'Hidden'}</span><div className="admin-actions"><Button onClick={()=>publish('tracks',t.id)}>{t.is_active?'Hide':'Show'} track</Button></div></Card>)}</div>
  <h2>Courses 📚</h2><div className="course-grid">{courses.map(c=><Card key={c.id}><h3>{c.name}</h3><p>{c.description}</p><span className="age-pill">{c.is_published?'Published':'Draft'}</span>{c.fee>0&&<span className="age-pill coupon-pill">Fee {c.fee} — coupon required</span>}<div className="admin-actions"><Button onClick={()=>publish('courses',c.id)}>{c.is_published?'Unpublish':'Publish'} course</Button></div></Card>)}</div>
  <h2>Coupons 🎟️</h2>
  <Card>
   <p>No payment integration yet — a valid, active coupon grants free enrollment into any course with a fee. <code>FREE</code> is seeded with unlimited redemptions.</p>
   <form className="coupon-form" onSubmit={createCoupon}>
    <input className="kids-input" value={newCode} onChange={e=>setNewCode(e.target.value)} placeholder="New code (e.g. SUMMER2026)" required />
    <input className="kids-input" type="number" min="1" value={newMax} onChange={e=>setNewMax(e.target.value)} placeholder="Max redemptions (blank = unlimited)" />
    <Button type="submit" disabled={couponBusy}>{couponBusy?'Creating…':'Create coupon'}</Button>
   </form>
  </Card>
  <div className="course-grid">{coupons.map(cp=><Card key={cp.id}><h3>{cp.code}</h3><p>{cp.description||'No description'}</p><span className="age-pill">{cp.is_active?'Active':'Inactive'}</span><p className="coupon-usage">{cp.times_redeemed} redeemed{cp.max_redemptions!=null?` / ${cp.max_redemptions} max`:' (unlimited)'}</p><div className="admin-actions"><Button onClick={()=>toggleCoupon(cp)}>{cp.is_active?'Deactivate':'Activate'}</Button></div></Card>)}</div>
  <ContentStudio/>
 </main>
}
