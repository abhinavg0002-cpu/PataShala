import os
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint,
                        create_engine, event)
from sqlalchemy.orm import declarative_base, sessionmaker

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "app.db"))
os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def _pragmas(conn, _):
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL")      # several phones read while one writes
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()


Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()


class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    teacher_code = Column(String, nullable=False)   # issued by the school; proves a teacher belongs here


class Branch(Base):
    __tablename__ = "branches"
    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    name = Column(String, nullable=False)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("branch_id", "class_no", "section", "roll_no", name="uq_roll"),)
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)       # short code shown on the ID card
    uuid = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)                    # student | teacher
    name = Column(String, nullable=False)
    pin_hash = Column(String, nullable=False)
    pin_salt = Column(String, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    roll_no = Column(String)
    class_no = Column(Integer)
    section = Column(String)
    phone = Column(String, unique=True)                      # teachers: 10-digit mobile, can be used to log in
    gender = Column(String)
    board = Column(String)
    state = Column(String)
    area_type = Column(String)
    locality = Column(String)
    progress = Column(Text, default="{}")                    # JSON: academic-year status per subject
    demo_role = Column(String)                               # synthetic demo personas only
    created = Column(DateTime, default=datetime.utcnow)


class TeachingAssignment(Base):
    __tablename__ = "assignments"
    __table_args__ = (UniqueConstraint("teacher_id", "branch_id", "subject", "class_no", "section"),)
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    subject = Column(String, nullable=False)
    class_no = Column(Integer, nullable=False)
    section = Column(String, nullable=False)
    progress = Column(Text, default="{}")                    # JSON: what the teacher is teaching now


class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    subject = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")   # pending | approved | rejected | ended
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)


class Attempt(Base):
    __tablename__ = "attempts"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject = Column(String, nullable=False)
    question_id = Column(String, nullable=False)
    concept = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    load = Column(String, nullable=False)
    pair = Column(String)
    chosen = Column(Integer, nullable=False)
    correct = Column(Boolean, nullable=False)
    tag = Column(String)
    time_ms = Column(Integer, nullable=False)
    hint = Column(Integer, nullable=False, default=0)
    support = Column(String)
    mode = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String, nullable=False)
    concept = Column(String, nullable=False)
    note = Column(String)
    after_attempt_id = Column(Integer, nullable=False)
    done = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.utcnow)


class Decision(Base):
    __tablename__ = "decisions"
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String, nullable=False)
    concept = Column(String, nullable=False)
    system_cause = Column(String, nullable=False)
    action = Column(String, nullable=False)                  # confirm | override
    final_cause = Column(String, nullable=False)
    note = Column(String)
    created = Column(DateTime, default=datetime.utcnow)


class AuthSession(Base):
    __tablename__ = "sessions"
    token_hash = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created = Column(DateTime, default=datetime.utcnow)


def init():
    Base.metadata.create_all(engine)
