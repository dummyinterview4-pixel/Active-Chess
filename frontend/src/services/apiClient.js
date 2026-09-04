import axios from 'axios';
const api = axios.create({ baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000', headers: {'Content-Type':'application/json'} });
api.interceptors.request.use(config => { const token=localStorage.getItem('active_chess_token'); if(token) config.headers.Authorization=`Bearer ${token}`; return config; });
api.interceptors.response.use(r=>r, err=>{ if(err.response?.status===401) localStorage.removeItem('active_chess_token'); return Promise.reject(err); });
export default api;
