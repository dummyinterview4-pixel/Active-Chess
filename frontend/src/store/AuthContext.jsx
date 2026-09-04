import {createContext,useContext,useEffect,useState} from 'react';
import api from '../services/apiClient';
const AuthContext=createContext(null);
export function AuthProvider({children}){
 const [user,setUser]=useState(null); const [loading,setLoading]=useState(true);
 useEffect(()=>{
  const token=localStorage.getItem('active_chess_token');
  if(!token){setLoading(false);return;}
  api.get('/auth/me').then(r=>setUser(r.data)).catch(()=>{localStorage.removeItem('active_chess_token');setUser(null)}).finally(()=>setLoading(false));
 },[]);
 const login=async(username,password)=>{
  try{
   const body=new URLSearchParams({username,password});
   const r=await api.post('/auth/login',body,{headers:{'Content-Type':'application/x-www-form-urlencoded'}});
   localStorage.setItem('active_chess_token',r.data.access_token);
   const me=await api.get('/auth/me'); setUser(me.data); return me.data;
  }catch(err){localStorage.removeItem('active_chess_token');setUser(null);throw err;}
 };
 const register=async(data)=>{await api.post('/auth/register',data);return login(data.username,data.password)};
 const logout=()=>{localStorage.removeItem('active_chess_token');setUser(null)};
 return <AuthContext.Provider value={{user,loading,login,register,logout}}>{children}</AuthContext.Provider>
}
export const useAuth=()=>useContext(AuthContext);
