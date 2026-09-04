import {BrowserRouter,Routes,Route,Navigate} from 'react-router-dom';
import {useAuth, AuthProvider} from '../store/AuthContext';
import Header from '../components/layout/Header';
import AuthPage from '../features/auth/AuthPage';
import Dashboard from '../features/dashboard/Dashboard';
import CoursePage from '../features/courses/CoursePage';
import LessonPage from '../features/learning/LessonPage';
import AdminPage from '../features/admin/AdminPage';
import ProfilePage from '../features/profile/ProfilePage';
import MasterGamesPage from '../features/games/MasterGamesPage';
import CoachDashboard from '../features/coach/CoachDashboard';
import ParentDashboard from '../features/parent/ParentDashboard';
import Home from '../pages/Home';
import TrainingPlanPage from '../features/training-plan/TrainingPlanPage';
import SyllabusPage from '../features/syllabus/SyllabusPage';
function Protected({children}){const {user,loading}=useAuth();if(loading)return <div className="loading-screen">♞<span>Setting up your board…</span></div>;return user?children:<Navigate to="/login" replace/>}
function AppContent(){return <><Header/><Routes><Route path="/login" element={<AuthPage/>}/><Route path="/register" element={<AuthPage/>}/><Route path="/" element={<Home/>}/><Route path="/training-plan" element={<TrainingPlanPage/>}/><Route path="/syllabus" element={<SyllabusPage/>}/><Route path="/dashboard" element={<Protected><Dashboard/></Protected>}/><Route path="/courses/:courseId" element={<Protected><CoursePage/></Protected>}/><Route path="/lessons/:lessonId" element={<Protected><LessonPage/></Protected>}/><Route path="/profile" element={<Protected><ProfilePage/></Protected>}/><Route path="/admin" element={<Protected><AdminPage/></Protected>}/><Route path="/master-games" element={<Protected><MasterGamesPage/></Protected>}/><Route path="/coach" element={<Protected><CoachDashboard/></Protected>}/><Route path="/parent" element={<Protected><ParentDashboard/></Protected>}/><Route path="*" element={<Navigate to="/" replace/>}/></Routes></>}
export default function App(){return <AuthProvider><BrowserRouter><AppContent/></BrowserRouter></AuthProvider>}
