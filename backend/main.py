import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from dotenv import load_dotenv
from .database import Base, engine, get_db
from .models import Teacher, TrainingEvent
from .schemas import TeacherRegister, LoginRequest, EventCreate
from .auth import hash_password, verify_password, create_token, current_teacher, admin_teacher

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=os.getenv("APP_NAME", "DAV Teacher Training Portal"), version="1.0.0", lifespan=lifespan)
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins or ["http://localhost:5500"],
                   allow_credentials=True, allow_methods=["GET", "POST", "PATCH"], allow_headers=["*"])

@app.get("/")
def health():
    return {"status": "ok", "app": "DAV Teacher Training Portal"}

@app.post("/api/auth/register", status_code=201)
def register(data: TeacherRegister, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.scalar(select(Teacher).where(Teacher.email == email)):
        raise HTTPException(409, "This email is already registered.")
    if db.scalar(select(Teacher).where(Teacher.mobile == data.mobile)):
        raise HTTPException(409, "This mobile number is already registered.")
    teacher = Teacher(full_name=data.full_name, email=email, mobile=data.mobile,
                      whatsapp=data.whatsapp, school=data.school,
                      subjects=", ".join(data.subjects), levels=", ".join(data.levels),
                      password_hash=hash_password(data.password), status="Pending")
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return {"message": "Registration submitted. Your account is Pending approval.", "teacher_id": teacher.id}

@app.post("/api/auth/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    teacher = db.scalar(select(Teacher).where(Teacher.email == data.email.lower()))
    if not teacher or not verify_password(data.password, teacher.password_hash):
        raise HTTPException(401, "Invalid email or password.")
    if teacher.status != "Approved" and not teacher.is_admin:
        raise HTTPException(403, "Your account is pending approval. Please contact the administrator.")
    return {"access_token": create_token(teacher), "token_type": "bearer",
            "teacher": {"id": teacher.id, "name": teacher.full_name, "email": teacher.email, "is_admin": teacher.is_admin}}

@app.get("/api/teachers/me")
def my_profile(teacher: Teacher = Depends(current_teacher)):
    return {"id": teacher.id, "full_name": teacher.full_name, "email": teacher.email,
            "mobile": teacher.mobile, "whatsapp": teacher.whatsapp, "school": teacher.school,
            "subjects": teacher.subjects, "levels": teacher.levels, "status": teacher.status}

@app.get("/api/admin/teachers")
def list_teachers(_: Teacher = Depends(admin_teacher), db: Session = Depends(get_db)):
    rows = db.scalars(select(Teacher).order_by(Teacher.created_at.desc())).all()
    return [{"id": t.id, "name": t.full_name, "email": t.email, "mobile": t.mobile,
             "school": t.school, "subjects": t.subjects, "levels": t.levels,
             "status": t.status, "created_at": t.created_at.isoformat()} for t in rows]

@app.patch("/api/admin/teachers/{teacher_id}/status")
def update_status(teacher_id: int, status_value: str, _: Teacher = Depends(admin_teacher),
                  db: Session = Depends(get_db)):
    if status_value not in ("Pending", "Approved", "Rejected"):
        raise HTTPException(400, "Status must be Pending, Approved or Rejected.")
    teacher = db.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(404, "Teacher not found.")
    teacher.status = status_value
    db.commit()
    return {"message": f"Teacher status changed to {status_value}."}

@app.get("/api/trainings")
def get_trainings(db: Session = Depends(get_db)):
    rows = db.scalars(select(TrainingEvent).order_by(TrainingEvent.training_date.desc())).all()
    return [{"id": e.id, "title": e.title, "description": e.description, "date": e.training_date,
             "venue": e.venue, "subject": e.subject, "level": e.level} for e in rows]

@app.post("/api/admin/trainings", status_code=201)
def create_training(data: EventCreate, _: Teacher = Depends(admin_teacher), db: Session = Depends(get_db)):
    event = TrainingEvent(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"message": "Training event created.", "id": event.id}
