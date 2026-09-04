from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.config import settings
from app.core.exceptions import AppException
from app.core.error_handlers import app_exception_handler, validation_exception_handler, integrity_error_handler, generic_exception_handler
from app.routes.puzzles import router as puzzles_router
from app.routes.quizzes import router as quizzes_router
from app.routes.gamification import router as gamification_router
from app.routes.profile import router as profile_router
from app.routes import auth, learning, admin
from app.routes.master_games import router as master_games_router
from app.routes.main_set6 import router as set6_router
from app.routes.training_plan import router as training_plan_router
from app.routes.syllabus import router as syllabus_router
app=FastAPI(title='Active-Chess API', version='0.3.0')
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(learning.router, tags=['learning'])
app.include_router(admin.router, tags=['admin'])
@app.get('/')
def root(): return {'service':'active-chess','version':'0.3.0','docs':'/docs'}

@app.get('/health')
def health(): return {'status':'ok','service':'active-chess','version':'0.3.0'}

app.include_router(puzzles_router)
app.include_router(quizzes_router)
app.include_router(gamification_router)
app.include_router(profile_router)
app.include_router(master_games_router)
app.include_router(set6_router)
app.include_router(training_plan_router)
app.include_router(syllabus_router)
