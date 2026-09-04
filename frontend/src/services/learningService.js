import api from './apiClient';
export const getTracks = () => api.get('/tracks');
export const getCourses = (trackId) => api.get('/courses', { params: trackId ? { track_id: trackId } : {} });
export const getCourse = (id) => api.get(`/courses/${id}`);
export const getChapters = (courseId) => api.get(`/courses/${courseId}/chapters`);
export const getLessons = (chapterId) => api.get(`/chapters/${chapterId}/lessons`);
export const getLesson = (lessonId) => api.get(`/lessons/${lessonId}`);
export const getCourseProgress = (courseId) => api.get(`/courses/${courseId}/progress`);
export const enroll = (courseId, couponCode) => api.post('/enrollments', {
  course_id: courseId,
  ...(couponCode ? { coupon_code: couponCode } : {}),
});
export const completeLesson = (lessonId) => api.post(`/lessons/${lessonId}/complete`);

export const getNextLesson = () => api.get('/me/next-lesson');

export const getQuizzes = (lessonId) => api.get(`/quizzes/lesson/${lessonId}`);
export const attemptQuiz = (questionId, selectedOption) => api.post(`/quizzes/${questionId}/attempt`, { selected_option: selectedOption });

export const getMyStats = () => api.get('/me/stats');
export const getAllBadges = () => api.get('/badges');
export const getMyBadges = () => api.get('/me/badges');

export const getMyProfile = () => api.get('/me/profile');
export const updateMyProfile = (data) => api.put('/me/profile', data);

export const getAdminLessons = () => api.get('/admin/lessons');
export const getAdminPuzzles = (lessonId) => api.get('/admin/puzzles', { params: lessonId ? { lesson_id: lessonId } : {} });
export const createAdminPuzzle = (data) => api.post('/admin/puzzles', data);
export const updateAdminPuzzle = (id, data) => api.put(`/admin/puzzles/${id}`, data);
export const deleteAdminPuzzle = (id) => api.delete(`/admin/puzzles/${id}`);

export const getAdminQuizzes = (lessonId) => api.get('/admin/quizzes', { params: lessonId ? { lesson_id: lessonId } : {} });
export const createAdminQuiz = (data) => api.post('/admin/quizzes', data);
export const updateAdminQuiz = (id, data) => api.put(`/admin/quizzes/${id}`, data);
export const deleteAdminQuiz = (id) => api.delete(`/admin/quizzes/${id}`);

export const getRecommendations = () => api.get('/me/recommendations');
export const getMasterGames = () => api.get('/master-games');

export const getAdminCoupons = () => api.get('/admin/coupons');
export const createAdminCoupon = (data) => api.post('/admin/coupons', data);
export const updateAdminCoupon = (id, data) => api.patch(`/admin/coupons/${id}`, data);

// 3-Year Structured Training Plan (migrated from V16's studyPlan.js).
// The plan content is public static reference data; only the checkbox
// state against it requires auth.
export const getTrainingPlan = () => api.get('/training-plan');
export const getTrainingPlanProgress = () => api.get('/training-plan/progress');
export const getTrainingPlanStats = () => api.get('/training-plan/stats');
export const markTrainingPlanItem = (itemKey) => api.put(`/training-plan/progress/${itemKey}`);
export const unmarkTrainingPlanItem = (itemKey) => api.delete(`/training-plan/progress/${itemKey}`);

// Syllabus tracks (migrated from V16's syllabusData.js) — descriptive
// curriculum-overview content, public.
export const getSyllabusTracks = () => api.get('/syllabus-tracks');
