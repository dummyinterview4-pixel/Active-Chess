import {useAuth} from '../../store/AuthContext';
import {Link} from 'react-router-dom';

export default function Header(){
 const {user,logout}=useAuth();
 return <header className="kids-header">
  <Link className="brand-kids" to={user?'/dashboard':'/'}><span className="brand-bubble">♞</span><div><b>ACTIVE-CHESS</b><small>Play • Learn • Grow</small></div></Link>
  <div className="header-right">
   <Link className="header-public-link" to="/training-plan">3-Year Plan 🗺️</Link>
   <Link className="header-public-link" to="/syllabus">Syllabus 🧭</Link>
   {user?<>
   <Link className="profile-link" to="/profile">Hi, {user.full_name||user.username}! 👋</Link>
   <Link className="admin-link" to="/dashboard">My learning</Link>
   {['admin','coach','trainer'].includes(user.role)&&<Link className="admin-link" to="/coach">Students 🧑‍🏫</Link>}
   {user.role==='parent'&&<Link className="admin-link" to="/parent">Family 👨‍👩‍👧</Link>}
   {user.role==='admin'&&<Link className="admin-link" to="/admin">Coach Studio 🧑‍🏫</Link>}
   <button className="logout" onClick={logout}>Log out</button>
  </>:<><Link className="header-public-link" to="/login">Sign in</Link><Link className="kids-btn header-signup" to="/register">Join Active-Chess →</Link></>}</div>
 </header>
}
