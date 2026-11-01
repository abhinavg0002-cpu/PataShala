"""FastAPI backend. Every role rule is enforced HERE, not only in the app screens."""
import json
import os
import secrets
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func

from . import bank, catalog as cat, db as D, engine as E, security as S, sim

DEMO_SUBJECTS = {s["id"] for s in cat.SUBJECTS if s["enabled"]}
DEMO_CLASS = 8
SECTIONS = ["A", "B", "C", "D"]


@asynccontextmanager
async def lifespan(app):
    D.init()
    from . import seed
    seed.run_if_empty()
    yield


app = FastAPI(title="PataShala API", lifespan=lifespan)
# CORS only matters for the web preview used in testing; phones (Expo Go) do not use it. No cookies are used.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def get_db():
    s = D.Session()
    try:
        yield s
    finally:
        s.close()


def current_user(authorization: Optional[str] = Header(None), db=Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Please log in.")
    row = db.get(D.AuthSession, S.token_hash(authorization[7:]))
    if not row:
        raise HTTPException(401, "Session expired. Please log in again.")
    return db.get(D.User, row.user_id)


def student_only(u=Depends(current_user)):
    if u.role != "student":
        raise HTTPException(403, "Students only.")
    return u


def teacher_only(u=Depends(current_user)):
    if u.role != "teacher":
        raise HTTPException(403, "Teachers only.")
    return u


def user_json(u, db):
    sch, br = db.get(D.School, u.school_id), db.get(D.Branch, u.branch_id)
    return {"id": u.id, "code": u.code, "uuid": u.uuid, "role": u.role, "name": u.name, "school": sch.name,
            "branch": br.name, "roll_no": u.roll_no, "class_no": u.class_no, "section": u.section,
            "phone": u.phone, "gender": u.gender, "board": u.board, "state": u.state, "area_type": u.area_type,
            "locality": u.locality, "demo_persona": u.demo_role}


def login_response(u, db):
    tok, h = S.new_token()
    db.add(D.AuthSession(token_hash=h, user_id=u.id))
    db.commit()
    return {"token": tok, "user": user_json(u, db)}


def new_code(db, prefix):
    while True:
        c = prefix + str(secrets.randbelow(90000) + 10000)
        if not db.query(D.User).filter_by(code=c).first():
            return c


# ---------------------------------------------------------------- public
@app.get("/health")
def health():
    return {"ok": True, "time": datetime.utcnow().isoformat()}


@app.get("/meta/catalog")
def meta_catalog():
    return cat.public_catalog()


@app.get("/schools")
def schools(db=Depends(get_db)):
    out = []
    for s in db.query(D.School).all():
        out.append({"id": s.id, "name": s.name,
                    "branches": [{"id": b.id, "name": b.name} for b in db.query(D.Branch).filter_by(school_id=s.id)]})
    return out


class Login(BaseModel):
    code: str
    pin: str


@app.post("/auth/login")
def login(b: Login, db=Depends(get_db)):
    code = b.code.strip().upper()
    if S.locked(code):
        raise HTTPException(429, "Too many wrong tries. Wait a minute and try again.")
    u = (db.query(D.User).filter_by(phone=code, role="teacher").first() if code.isdigit()
         else db.query(D.User).filter_by(code=code).first())
    if not u or not S.check_pin(b.pin, u.pin_hash, u.pin_salt):
        S.fail(code)
        raise HTTPException(401, "Wrong ID or PIN.")
    S.ok(code)
    return login_response(u, db)


@app.get("/me")
def me(u=Depends(current_user), db=Depends(get_db)):
    return user_json(u, db)


class ChangePin(BaseModel):
    old_pin: str = Field(pattern=r"^\d{4}$")
    new_pin: str = Field(pattern=r"^\d{4}$")


@app.post("/me/change-pin")
def change_pin(b: ChangePin, u=Depends(current_user), db=Depends(get_db)):
    if not S.check_pin(b.old_pin, u.pin_hash, u.pin_salt):
        raise HTTPException(401, "The current PIN is wrong.")
    u.pin_hash, u.pin_salt = S.hash_pin(b.new_pin)
    db.commit()
    return {"ok": True}


class ResetPin(BaseModel):
    who: str = Field(min_length=3, max_length=20)          # teacher: mobile number or ID; student: ID
    new_pin: str = Field(pattern=r"^\d{4}$")
    teacher_code: str = ""                                  # teachers: the school's teacher code
    roll_no: str = ""                                       # students: roll number and section
    section: str = ""


@app.post("/auth/reset-pin")
def reset_pin(b: ResetPin, db=Depends(get_db)):
    """Forgot PIN. shortcut: identity is checked with details the person already knows (school code, or roll number
    and section), not an SMS code, because SMS needs a paid gateway and internet. Upgrade to a one-time code for real use."""
    key = b.who.strip().upper()
    if S.locked(key):
        raise HTTPException(429, "Too many tries. Wait a minute and try again.")
    u = (db.query(D.User).filter_by(phone=key, role="teacher").first() if key.isdigit() else db.query(D.User).filter_by(code=key).first())
    sch = db.get(D.School, u.school_id) if u else None
    ok = bool(u) and (
        (u.role == "teacher" and secrets.compare_digest(b.teacher_code.strip().upper(), sch.teacher_code.upper()))
        or (u.role == "student" and b.roll_no.strip() == (u.roll_no or "-") and b.section.strip().upper() == (u.section or "-")))
    if not ok:
        S.fail(key)
        raise HTTPException(403, "Those details do not match. Check them and try again.")
    S.ok(key)
    u.pin_hash, u.pin_salt = S.hash_pin(b.new_pin)
    db.commit()
    return {"ok": True}


# ---------------------------------------------------------------- registration
class Assign(BaseModel):
    subject: str
    class_no: int
    section: str


class TeacherReg(BaseModel):
    school_id: int
    branch_id: int
    teacher_code: str
    name: str = Field(min_length=2, max_length=60)
    phone: str = Field(pattern=r"^\d{10}$")
    pin: str = Field(pattern=r"^\d{4}$")
    assignments: list[Assign] = Field(min_length=1, max_length=12)


def _check_branch(db, school_id, branch_id):
    br = db.get(D.Branch, branch_id)
    if not br or br.school_id != school_id:
        raise HTTPException(422, "That branch does not belong to the chosen school.")


def _check_scope(subject, class_no, section):
    if subject not in DEMO_SUBJECTS:
        raise HTTPException(422, "That subject is not available in this demo.")
    if class_no != DEMO_CLASS:
        raise HTTPException(422, "Only Class 8 is available in this demo.")
    if section not in SECTIONS:
        raise HTTPException(422, "Section must be A, B, C or D.")


class CodeCheck(BaseModel):
    school_id: int
    branch_id: int
    teacher_code: str
    phone: str = ""                  # optional: also tell the teacher now if this number is already taken


def _check_code(db, school_id, branch_id, code):
    sch = db.get(D.School, school_id)
    if not sch:
        raise HTTPException(422, "Unknown school.")
    _check_branch(db, school_id, branch_id)
    key = f"school{school_id}"                       # shortcut: per-school guess limit, resets on restart
    if S.locked(key):
        raise HTTPException(429, "Too many wrong codes. Wait a minute and try again.")
    if not secrets.compare_digest(code.strip().upper(), sch.teacher_code.upper()):
        S.fail(key)
        raise HTTPException(403, "Wrong teacher code. Ask your school office for the teacher code.")
    S.ok(key)


@app.post("/register/check-code")
def register_check_code(b: CodeCheck, db=Depends(get_db)):
    """Lets the app tell the teacher right away whether the school code is right."""
    _check_code(db, b.school_id, b.branch_id, b.teacher_code)
    if b.phone and db.query(D.User).filter_by(phone=b.phone).first():
        raise HTTPException(409, "That mobile number is already registered. Log in with it, or use Forgot PIN.")
    return {"ok": True}


@app.post("/register/teacher")
def register_teacher(b: TeacherReg, db=Depends(get_db)):
    _check_code(db, b.school_id, b.branch_id, b.teacher_code)
    seen = set()
    for a in b.assignments:
        _check_scope(a.subject, a.class_no, a.section)
        if (a.subject, a.class_no, a.section) in seen:
            raise HTTPException(422, "The same subject, class and section is listed twice.")
        seen.add((a.subject, a.class_no, a.section))
    if db.query(D.User).filter_by(phone=b.phone).first():
        raise HTTPException(409, "That mobile number is already registered. Log in instead, or use Forgot PIN.")
    h, salt = S.hash_pin(b.pin)
    u = D.User(code=new_code(db, "T"), uuid=secrets.token_hex(16), role="teacher", name=b.name.strip(), pin_hash=h,
               pin_salt=salt, school_id=b.school_id, branch_id=b.branch_id, phone=b.phone)
    db.add(u)
    db.flush()
    for a in b.assignments:
        db.add(D.TeachingAssignment(teacher_id=u.id, branch_id=b.branch_id, subject=a.subject, class_no=a.class_no, section=a.section))
    db.commit()
    return login_response(u, db)


class StudentReg(BaseModel):
    school_id: int
    branch_id: int
    name: str = Field(min_length=2, max_length=60)
    roll_no: str = Field(pattern=r"^\d{1,4}$")
    class_no: int
    section: str
    gender: str
    board: str
    state: str
    area_type: str = ""
    locality: str = Field(default="", max_length=60)
    pin: str = Field(pattern=r"^\d{4}$")


@app.post("/register/student")
def register_student(b: StudentReg, db=Depends(get_db)):
    if not db.get(D.School, b.school_id):
        raise HTTPException(422, "Unknown school.")
    _check_branch(db, b.school_id, b.branch_id)
    if b.class_no != DEMO_CLASS or b.section not in SECTIONS:
        raise HTTPException(422, "Only Class 8, sections A–D are available in this demo.")
    if b.board != "telangana" or b.state != "telangana":
        raise HTTPException(422, "Only the Telangana State Board in Telangana is available in this demo.")
    if b.gender not in ("Girl", "Boy", "Other"):
        raise HTTPException(422, "Choose a gender option.")
    if b.area_type and b.area_type not in cat.AREA_TYPES:
        raise HTTPException(422, "Choose an area type.")
    if db.query(D.User).filter_by(branch_id=b.branch_id, class_no=b.class_no, section=b.section, roll_no=b.roll_no).first():
        raise HTTPException(409, "That roll number is already registered in this class and section.")
    h, salt = S.hash_pin(b.pin)
    u = D.User(code=new_code(db, "S"), uuid=secrets.token_hex(16), role="student", name=b.name.strip(), pin_hash=h,
               pin_salt=salt, school_id=b.school_id, branch_id=b.branch_id, roll_no=b.roll_no, class_no=b.class_no,
               section=b.section, gender=b.gender, board=b.board, state=b.state, area_type=b.area_type,
               locality=b.locality.strip())
    db.add(u)
    db.commit()
    return login_response(u, db)


# ---------------------------------------------------------------- shared helpers
def attempts_of(db, student_id, subject):
    rows = db.query(D.Attempt).filter_by(student_id=student_id, subject=subject).order_by(D.Attempt.id).all()
    return [{"question_id": r.question_id, "concept": r.concept, "difficulty": r.difficulty, "load": r.load,
             "pair": r.pair, "correct": r.correct, "tag": r.tag, "time_ms": r.time_ms, "hint": r.hint,
             "support": r.support, "mode": r.mode, "id": r.id, "created": r.created} for r in rows]


def open_tasks(db, student_id, subject):
    """Teacher-assigned concepts still open. A task closes after 3 practice answers on that concept."""
    out = []
    for t in db.query(D.Task).filter_by(student_id=student_id, subject=subject, done=False).order_by(D.Task.id):
        n = db.query(D.Attempt).filter(D.Attempt.student_id == student_id, D.Attempt.concept == t.concept,
                                       D.Attempt.mode == "practice", D.Attempt.id > t.after_attempt_id).count()
        if n >= 3:
            t.done = True
        else:
            out.append(t.concept)
    db.commit()
    return out


def concept_cards(an):
    out = []
    for cid in cat.SUBJECT_CONCEPTS[an["subject"]]:
        c, st = cat.CONCEPT[cid], an["statuses"][cid]
        causes = []
        for x in an["causes"][cid]:
            y = dict(x)
            if x["type"] == "prerequisite":
                y["prereq_name"] = cat.CONCEPT[x["prereq"]]["name"]
            if x["type"] == "misconception":
                y["fix"] = cat.TAGS[x["tag"]][1]
            causes.append(y)
        out.append({"id": cid, "name": c["name"], "subtopic": c["subtopic"], "main": c["main"], "prereq": c["prereq"],
                    "status": "needs_support" if st["weak_probe"] else st["status"], "score": st["score"], "n": st["n"],
                    "causes": causes})
    return out


def validate_subject(subject):
    if subject not in DEMO_SUBJECTS:
        raise HTTPException(422, "That subject is not available in this demo.")


# ---------------------------------------------------------------- student
@app.get("/student/subjects")
def student_subjects(u=Depends(student_only), db=Depends(get_db)):
    prog = json.loads(u.progress or "{}")
    out = []
    for s in cat.SUBJECTS:
        row = {"id": s["id"], "name": s["name"], "enabled": s["enabled"]}
        if s["enabled"]:
            en = (db.query(D.Enrollment).filter(D.Enrollment.student_id == u.id, D.Enrollment.subject == s["id"],
                                                D.Enrollment.status.in_(["pending", "approved"])).order_by(D.Enrollment.id.desc()).first())
            row["enrollment"] = None
            if en:
                a = db.get(D.TeachingAssignment, en.assignment_id)
                row["enrollment"] = {"status": en.status, "teacher": db.get(D.User, a.teacher_id).name}
            row["progress"] = prog.get(s["id"])
            an = E.analyse(s["id"], attempts_of(db, u.id, s["id"]))
            row["diagnostic_done"] = an["diagnostic_done"]
            row["level"] = an["level"]
            row["counts"] = an["counts"]
            row["answered"] = an["answered"]
        out.append(row)
    return out


@app.get("/student/options")
def student_options(subject: str, u=Depends(student_only), db=Depends(get_db)):
    validate_subject(subject)
    rows = db.query(D.TeachingAssignment).filter_by(branch_id=u.branch_id, subject=subject, class_no=u.class_no, section=u.section).all()
    return [{"assignment_id": a.id, "teacher": db.get(D.User, a.teacher_id).name, "section": a.section,
             "class_no": a.class_no, "teaching": json.loads(a.progress or "{}")} for a in rows]


class Enroll(BaseModel):
    subject: str
    assignment_id: int


@app.post("/student/enroll")
def student_enroll(b: Enroll, u=Depends(student_only), db=Depends(get_db)):
    validate_subject(b.subject)
    a = db.get(D.TeachingAssignment, b.assignment_id)
    if not a or (a.branch_id, a.subject, a.class_no, a.section) != (u.branch_id, b.subject, u.class_no, u.section):
        raise HTTPException(422, "That teacher does not teach this subject to your class and section.")
    for old in db.query(D.Enrollment).filter(D.Enrollment.student_id == u.id, D.Enrollment.subject == b.subject,
                                             D.Enrollment.status.in_(["pending", "approved"])):
        old.status, old.end_date = "ended", datetime.utcnow()
    en = D.Enrollment(student_id=u.id, assignment_id=a.id, subject=b.subject, status="pending")
    db.add(en)
    db.commit()
    return {"status": "pending", "teacher": db.get(D.User, a.teacher_id).name}


class Progress(BaseModel):
    subject: str
    year_status: str = Field(pattern="^(starting|ongoing)$")
    chapters_done: list[str] = []
    current_chapter: Optional[str] = None
    topic_reached: Optional[str] = None


@app.post("/student/progress")
def student_progress(b: Progress, u=Depends(student_only), db=Depends(get_db)):
    validate_subject(b.subject)
    prog = json.loads(u.progress or "{}")
    prog[b.subject] = {"book": cat.BOOK, "year_status": b.year_status, "chapters_done": b.chapters_done[:30],
                       "current_chapter": b.current_chapter, "topic_reached": b.topic_reached}
    u.progress = json.dumps(prog)
    db.commit()
    return {"ok": True}


@app.get("/student/next")
def student_next(subject: str, u=Depends(student_only), db=Depends(get_db)):
    validate_subject(subject)
    return E.next_step(subject, attempts_of(db, u.id, subject), open_tasks(db, u.id, subject))


class Answer(BaseModel):
    subject: str
    question_id: str
    chosen: int = Field(ge=0, le=3)
    time_ms: int = Field(ge=0, le=600000)
    hint: int = Field(default=0, ge=0, le=3)
    support: Optional[str] = None


@app.post("/student/answer")
def student_answer(b: Answer, u=Depends(student_only), db=Depends(get_db)):
    validate_subject(b.subject)
    atts = attempts_of(db, u.id, b.subject)
    step = E.next_step(b.subject, atts, open_tasks(db, u.id, b.subject))
    if step["question"] is None or step["question"]["id"] != b.question_id:
        raise HTTPException(409, "That is not the current question. Please reload.")
    q = bank.BY_ID[b.question_id]
    fb = E.mark(q, b.chosen)
    before = E.concept_status([a for a in atts if a["concept"] == q["concept"]])["status"]
    db.add(D.Attempt(student_id=u.id, subject=b.subject, question_id=q["id"], concept=q["concept"], difficulty=q["difficulty"],
                     load=q["load"], pair=q["pair"], chosen=b.chosen, correct=fb["correct"], tag=fb["tag"],
                     time_ms=b.time_ms, hint=b.hint, support=step["support"], mode=step["phase"]))
    db.commit()
    after_atts = attempts_of(db, u.id, b.subject)
    nxt = E.next_step(b.subject, after_atts, open_tasks(db, u.id, b.subject))
    after = E.concept_status([a for a in after_atts if a["concept"] == q["concept"]])["status"]
    return {"feedback": fb, "concept": {"id": q["concept"], "name": cat.CONCEPT[q["concept"]]["name"], "before": before, "after": after},
            "next": nxt}


@app.get("/student/report")
def student_report(subject: str, u=Depends(student_only), db=Depends(get_db)):
    validate_subject(subject)
    an = E.analyse(subject, attempts_of(db, u.id, subject))
    return {"subject": subject, "level": an["level"], "baseline_score": an["baseline_score"], "answered": an["answered"],
            "diagnostic_done": an["diagnostic_done"], "counts": an["counts"], "language": an["language"],
            "thresholds": {"secure": E.SECURE, "developing": E.DEVELOPING, "weights": E.WEIGHT},
            "concepts": concept_cards(an), "what_helped": an["what_helped"], "flags": an["flags"]}


# ---------------------------------------------------------------- teacher
def visible(db, teacher, student_id, subject):
    """The ONE rule for 'may this teacher see this student': an approved enrollment with this teacher for this subject."""
    return (db.query(D.Enrollment).join(D.TeachingAssignment, D.Enrollment.assignment_id == D.TeachingAssignment.id)
            .filter(D.Enrollment.student_id == student_id, D.Enrollment.subject == subject, D.Enrollment.status == "approved",
                    D.TeachingAssignment.teacher_id == teacher.id).first())


def my_assignment(db, teacher, assignment_id):
    a = db.get(D.TeachingAssignment, assignment_id)
    if not a or a.teacher_id != teacher.id:
        raise HTTPException(404, "Class not found.")
    return a


def roster_students(db, a):
    rows = (db.query(D.Enrollment, D.User).join(D.User, D.User.id == D.Enrollment.student_id)
            .filter(D.Enrollment.assignment_id == a.id, D.Enrollment.status == "approved").order_by(D.User.roll_no).all())
    return [u for _, u in rows]


def primary_cause(an):
    for cid in cat.SUBJECT_CONCEPTS[an["subject"]]:
        if an["causes"][cid] and an["statuses"][cid]["status"] in ("needs_support", "developing") or (an["causes"][cid] and an["statuses"][cid]["weak_probe"]):
            c = an["causes"][cid][0]
            return {"concept": cat.CONCEPT[cid]["name"], "concept_id": cid, "type": c["type"], "label": c["label"]}
    return None


@app.get("/teacher/assignments")
def teacher_assignments(t=Depends(teacher_only), db=Depends(get_db)):
    out = []
    for a in db.query(D.TeachingAssignment).filter_by(teacher_id=t.id).order_by(D.TeachingAssignment.subject, D.TeachingAssignment.section):
        studs = roster_students(db, a)
        lv = {"Basic": 0, "Medium": 0, "Strong": 0, "Not tested": 0}
        weak = {}
        for s in studs:
            an = E.analyse(a.subject, attempts_of(db, s.id, a.subject))
            lv[an["level"] or "Not tested"] += 1
            for cid in cat.subject_main_concepts(a.subject):
                if an["statuses"][cid]["status"] == "needs_support" or an["statuses"][cid]["weak_probe"]:
                    weak[cid] = weak.get(cid, 0) + 1
        pending = db.query(D.Enrollment).filter_by(assignment_id=a.id, status="pending").count()
        out.append({"id": a.id, "subject": a.subject, "subject_name": next(s["name"] for s in cat.SUBJECTS if s["id"] == a.subject),
                    "class_no": a.class_no, "section": a.section, "students": len(studs), "pending": pending, "levels": lv,
                    "progress": json.loads(a.progress or "{}"),
                    "weakest": sorted([{"concept": cat.CONCEPT[c]["name"], "students": n} for c, n in weak.items()], key=lambda x: -x["students"])[:3]})
    return out


class TeachProgress(BaseModel):
    assignment_id: int
    year_status: str = Field(pattern="^(starting|ongoing)$")
    chapters_done: list[str] = []
    current_chapter: Optional[str] = None
    topic_reached: Optional[str] = None


@app.post("/teacher/assignment-progress")
def teacher_assignment_progress(b: TeachProgress, t=Depends(teacher_only), db=Depends(get_db)):
    a = my_assignment(db, t, b.assignment_id)
    a.progress = json.dumps({"book": cat.BOOK, "year_status": b.year_status, "chapters_done": b.chapters_done[:30],
                             "current_chapter": b.current_chapter, "topic_reached": b.topic_reached})
    db.commit()
    return {"ok": True}


@app.get("/teacher/requests")
def teacher_requests(t=Depends(teacher_only), db=Depends(get_db)):
    rows = (db.query(D.Enrollment, D.User, D.TeachingAssignment).join(D.User, D.User.id == D.Enrollment.student_id)
            .join(D.TeachingAssignment, D.TeachingAssignment.id == D.Enrollment.assignment_id)
            .filter(D.TeachingAssignment.teacher_id == t.id, D.Enrollment.status == "pending").all())
    return [{"id": e.id, "student": u.name, "code": u.code, "roll_no": u.roll_no, "subject": a.subject, "class_no": a.class_no,
             "section": a.section} for e, u, a in rows]


class Review(BaseModel):
    approve: bool


@app.post("/teacher/requests/{rid}")
def teacher_review(rid: int, b: Review, t=Depends(teacher_only), db=Depends(get_db)):
    e = db.get(D.Enrollment, rid)
    a = db.get(D.TeachingAssignment, e.assignment_id) if e else None
    if not e or a.teacher_id != t.id or e.status != "pending":
        raise HTTPException(404, "Request not found.")
    e.status = "approved" if b.approve else "rejected"
    db.commit()
    return {"status": e.status}


@app.get("/teacher/roster")
def teacher_roster(assignment_id: int, t=Depends(teacher_only), db=Depends(get_db)):
    a = my_assignment(db, t, assignment_id)
    concepts = [{"id": c, "name": cat.CONCEPT[c]["name"], "main": cat.CONCEPT[c]["main"]} for c in cat.SUBJECT_CONCEPTS[a.subject]]
    students = []
    for s in roster_students(db, a):
        an = E.analyse(a.subject, attempts_of(db, s.id, a.subject))
        wk = [cat.CONCEPT[c]["name"] for c in an["weak"] if cat.CONCEPT[c]["main"]]
        students.append({"id": s.id, "name": s.name, "code": s.code, "roll_no": s.roll_no, "level": an["level"],
                         "answered": an["answered"], "counts": an["counts"], "primary": primary_cause(an), "flags": an["flags"],
                         "weak": wk, "strong": [cat.CONCEPT[c]["name"] for c in an["strong"] if cat.CONCEPT[c]["main"]],
                         "statuses": {c: ("needs_support" if an["statuses"][c]["weak_probe"] else an["statuses"][c]["status"]) for c in an["statuses"]}})
    return {"assignment": {"id": a.id, "subject": a.subject, "class_no": a.class_no, "section": a.section}, "concepts": concepts, "students": students}


@app.get("/teacher/student")
def teacher_student(student_id: int, subject: str, t=Depends(teacher_only), db=Depends(get_db)):
    validate_subject(subject)
    if not visible(db, t, student_id, subject):
        raise HTTPException(403, "This student is not in your class for this subject.")
    s = db.get(D.User, student_id)
    atts = attempts_of(db, s.id, subject)
    an = E.analyse(subject, atts)
    decisions = db.query(D.Decision).filter_by(student_id=s.id, subject=subject, teacher_id=t.id).order_by(D.Decision.id.desc()).all()
    latest = {}
    for d in decisions:
        latest.setdefault(d.concept, {"action": d.action, "final_cause": d.final_cause, "note": d.note})
    cards = concept_cards(an)
    for c in cards:
        c["decision"] = latest.get(c["id"])
    hist = [{"concept": cat.CONCEPT[a["concept"]]["name"], "difficulty": a["difficulty"], "load": a["load"], "correct": a["correct"],
             "hint": a["hint"], "time_s": round(a["time_ms"] / 1000, 1), "support": a["support"], "mode": a["mode"]} for a in atts[-25:]]
    return {"student": {"id": s.id, "name": s.name, "code": s.code, "roll_no": s.roll_no, "section": s.section,
                        "progress": json.loads(s.progress or "{}").get(subject)},
            "level": an["level"], "baseline_score": an["baseline_score"], "counts": an["counts"], "language": an["language"],
            "thresholds": {"secure": E.SECURE, "developing": E.DEVELOPING, "weights": E.WEIGHT},
            "concepts": cards, "strengths": [cat.CONCEPT[c]["name"] for c in an["strong"]],
            "weaknesses": [cat.CONCEPT[c]["name"] for c in an["weak"]], "what_helped": an["what_helped"],
            "flags": an["flags"], "history": hist}


class Group(BaseModel):
    subject: str
    student_ids: list[int] = Field(min_length=1, max_length=60)


@app.post("/teacher/group")
def teacher_group(b: Group, t=Depends(teacher_only), db=Depends(get_db)):
    validate_subject(b.subject)
    weak, causes, names = {}, {}, []
    for sid in b.student_ids:
        if not visible(db, t, sid, b.subject):
            raise HTTPException(403, "One of the selected students is not in your class for this subject.")
        s = db.get(D.User, sid)
        names.append(s.name)
        an = E.analyse(b.subject, attempts_of(db, sid, b.subject))
        for cid in cat.SUBJECT_CONCEPTS[b.subject]:
            if an["statuses"][cid]["status"] == "needs_support" or an["statuses"][cid]["weak_probe"]:
                weak[cid] = weak.get(cid, 0) + 1
                if an["causes"][cid]:
                    k = an["causes"][cid][0]["label"]
                    causes[k] = causes.get(k, 0) + 1
    top = sorted(weak.items(), key=lambda x: -x[1])
    return {"count": len(b.student_ids), "names": names,
            "shared_weak": [{"concept_id": c, "concept": cat.CONCEPT[c]["name"], "students": n} for c, n in top],
            "causes": sorted([{"label": k, "count": n} for k, n in causes.items()], key=lambda x: -x["count"])}


class AssignTask(BaseModel):
    subject: str
    concept_id: str
    student_ids: list[int] = Field(min_length=1, max_length=60)
    note: str = Field(default="", max_length=120)


@app.post("/teacher/assign")
def teacher_assign(b: AssignTask, t=Depends(teacher_only), db=Depends(get_db)):
    validate_subject(b.subject)
    if b.concept_id not in cat.SUBJECT_CONCEPTS[b.subject]:
        raise HTTPException(422, "Unknown concept for this subject.")
    for sid in b.student_ids:
        if not visible(db, t, sid, b.subject):
            raise HTTPException(403, "One of the selected students is not in your class for this subject.")
    for sid in b.student_ids:
        last = db.query(func.max(D.Attempt.id)).filter_by(student_id=sid).scalar() or 0
        db.add(D.Task(student_id=sid, teacher_id=t.id, subject=b.subject, concept=b.concept_id, note=b.note, after_attempt_id=last))
    db.commit()
    return {"assigned": len(b.student_ids)}


class Decide(BaseModel):
    student_id: int
    subject: str
    concept_id: str
    system_cause: str
    action: str = Field(pattern="^(confirm|override)$")
    final_cause: str
    note: str = Field(default="", max_length=200)


CAUSE_TYPES = {"misconception", "language", "prerequisite", "gap", "slip"}


@app.post("/teacher/decision")
def teacher_decision(b: Decide, t=Depends(teacher_only), db=Depends(get_db)):
    validate_subject(b.subject)
    if not visible(db, t, b.student_id, b.subject):
        raise HTTPException(403, "This student is not in your class for this subject.")
    if b.system_cause not in CAUSE_TYPES or b.final_cause not in CAUSE_TYPES | {"none"}:
        raise HTTPException(422, "Unknown cause.")
    if b.action == "confirm" and b.final_cause != b.system_cause:
        raise HTTPException(422, "Confirm means the final cause equals the system's cause.")
    db.add(D.Decision(teacher_id=t.id, student_id=b.student_id, subject=b.subject, concept=b.concept_id,
                      system_cause=b.system_cause, action=b.action, final_cause=b.final_cause, note=b.note))
    db.commit()
    return {"ok": True}


@app.get("/teacher/stats")
def teacher_stats(t=Depends(teacher_only), db=Depends(get_db)):
    rows = db.query(D.Decision).filter_by(teacher_id=t.id).all()
    n, ok = len(rows), sum(1 for r in rows if r.action == "confirm")
    return {"decisions": n, "confirmed": ok, "overridden": n - ok, "accept_rate": None if n == 0 else round(ok / n, 2)}


# ---------------------------------------------------------------- demo helpers (synthetic data only)
_validation = {}


@app.get("/demo/validation")
def demo_validation():
    if not _validation:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "validation.json")
        if os.path.exists(path):
            _validation.update(json.load(open(path)))
        else:
            _validation.update(sim.validate())
    return _validation


@app.get("/demo/replay")
def demo_replay(question_id: str = "m_i2", db=Depends(get_db)):
    """Same question, three synthetic students. Next steps come from the real engine, not from a script."""
    q = bank.BY_ID.get(question_id)
    if not q:
        raise HTTPException(404, "Unknown question.")
    subject = cat.CONCEPT[q["concept"]]["subject"]
    wrong_tag = next((int(i) for i, tg in q["tags"].items() if tg), None)
    wrong_plain = next((i for i in range(4) if i != q["answer"] and str(i) != str(wrong_tag)), 0)
    personas = [("fast", "Fast student", q["answer"], 6000), ("misconception", "Student with a wrong idea", wrong_tag if wrong_tag is not None else wrong_plain, 9000),
                ("gap", "Student with an earlier-skill gap", wrong_plain, 12000)]
    out = []
    for role, label, chosen, ms in personas:
        u = db.query(D.User).filter_by(demo_role=role).first()
        if not u:
            continue
        atts = attempts_of(db, u.id, subject)
        before = E.concept_status([a for a in atts if a["concept"] == q["concept"]])
        fb = E.mark(q, chosen)
        hyp = {"question_id": q["id"], "concept": q["concept"], "difficulty": q["difficulty"], "load": q["load"], "pair": q["pair"],
               "correct": fb["correct"], "tag": fb["tag"], "time_ms": ms, "hint": 0, "support": None, "mode": "practice"}
        step = E.next_step(subject, atts + [hyp])
        after = E.concept_status([a for a in atts + [hyp] if a["concept"] == q["concept"]])
        out.append({"role": role, "label": label, "student": u.name, "chosen_text": q["options"][chosen], "correct": fb["correct"],
                    "tag_label": fb["tag_label"], "before": before["status"], "after": after["status"], "next": {
                        "stage": step["stage"], "concept": cat.CONCEPT[step["concept"]]["name"] if step["concept"] else None,
                        "difficulty": step["question"]["difficulty"] if step["question"] else None, "support": step["support"],
                        "lesson": bool(step["lesson"]), "trace": step["trace"]}})
    return {"question": {"id": q["id"], "text": q["text"], "options": q["options"], "difficulty": q["difficulty"], "concept": cat.CONCEPT[q["concept"]]["name"]},
            "subject": subject, "students": out}
