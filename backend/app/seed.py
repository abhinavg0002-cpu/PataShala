"""Synthetic demo data. Nobody here is real. All seeded accounts use PIN 1234 (demo only)."""
import json
import random
import secrets
from datetime import datetime, timedelta

from . import catalog as cat, db as D, security as S, sim

DEMO_PIN = "1234"
SCHOOL_CODE = "SH393511"             # school-issued teacher code: 2 letters of the school name + 6 digits (invented for this project)
SECOND_CODE = "LP960791"
SCHOOLS = [
    ("Sri Chaitanya School", "SC498373", ["Kukatpally", "Madhapur", "Gachibowli", "Dilsukhnagar", "Miyapur"]),
    ("Narayana School", "NA949330", ["Kukatpally", "Kondapur", "Secunderabad", "LB Nagar", "Nizampet"]),
    ("Oakridge International School", "OA944270", ["Gachibowli", "Bachupally"]),
    ("Delhi Public School", "DP544470", ["Nacharam", "Madhapur", "Gachibowli"]),
    ("Hyderabad Public School", "HP530084", ["Begumpet", "Ramanthapur"]),
    ("Glendale Academy", "GL317152", ["Nanakramguda", "Banjara Hills"]),
    ("Silver Oaks International School", "SO867393", ["Bachupally", "Kollur"]),
    ("Johnson Grammar School", "JG595882", ["Mehdipatnam", "Habsiguda"]),
    ("Chirec International School", "CH134614", ["Kondapur", "Gachibowli"]),
    ("Meridian School", "ME886833", ["Banjara Hills", "Madhapur", "Kukatpally"]),
]
NAMES = ["Aditya R.", "Bhavana S.", "Charan P.", "Divya N.", "Eshwar G.", "Farah K.", "Gowtham V.", "Harini M.",
         "Imran S.", "Jyothi D.", "Karthik B.", "Lavanya T.", "Manoj A.", "Nandini C.", "Omkar H.", "Pooja L."]


def _known(subject, **over):
    return sim.SimStudent(knows={c: True for c in cat.SUBJECT_CONCEPTS[subject]}, **{"slip": 0.0, **over})


def _personas():
    def broken(subject, concepts, mis=None):
        s = _known(subject)
        for c in concepts:
            s.knows[c] = False
        s.misconception = dict(mis or {})
        return s
    return {
        "fast": {s: _known(s) for s in ("maths", "physical", "biology")},
        "english": {"maths": _known("maths"), "physical": _known("physical", lang_penalty=0.5),
                    "biology": _known("biology", lang_penalty=0.95)},
        "gap": {"maths": broken("maths", ["m_ratio", "m_direct", "m_inverse", "m_compound"]),
                "physical": broken("physical", ["p_net"]), "biology": _known("biology")},
        "misconception": {"maths": broken("maths", ["m_inverse", "m_compound"], {"m_inverse": "treats_inverse_as_direct", "m_compound": "treats_inverse_as_direct"}),
                          "physical": broken("physical", ["p_net"], {"p_net": "zero_net_means_no_forces"}),
                          "biology": broken("biology", ["b_size"], {"b_size": "bigger_animal_bigger_cells"})},
    }


_pin_cache = {}


def _user(db, code, role, name, school, branch, pin=DEMO_PIN, **kw):
    if pin not in _pin_cache:
        _pin_cache[pin] = S.hash_pin(pin)
    h, salt = _pin_cache[pin]   # shortcut: seeded demo accounts share one hash (hashing 600 PINs takes ~40 s)
    u = D.User(code=code, uuid=secrets.token_hex(16), role=role, name=name, pin_hash=h, pin_salt=salt,
               school_id=school.id, branch_id=branch.id, **kw)
    db.add(u)
    db.flush()
    return u


def run_if_empty():
    db = D.Session()
    try:
        if db.query(D.School).count():
            return
        seed(db)
    finally:
        db.close()


def build_class(rng):
    """Make the synthetic classroom ONCE (18 Class 8 students with answer history); every branch then gets a copy."""
    people = [("Meera P.", "fast"), ("Kiran T.", "misconception"), ("Sana M.", "gap"), ("Ravi K.", "english")]
    people += [(NAMES[i], None) for i in range(6)]
    plan = [("A", n, r) for n, r in people] + [("B", NAMES[6 + i], None) for i in range(8)]
    personas = _personas()
    rolls = {"A": 0, "B": 0}
    base = datetime.utcnow() - timedelta(days=2)
    out = []
    for sec, name, role in plan:
        rolls[sec] += 1
        st = {"sec": sec, "name": name, "role": role, "roll": str(rolls[sec]), "gender": rng.choice(["Girl", "Boy"]),
              "area": rng.choice(cat.AREA_TYPES), "subjects": {}}
        for subj in ("maths", "physical", "biology"):
            student = personas[role][subj] if role else sim.random_hidden(subj, rng)[0]
            steps = {"fast": 1, "misconception": 1, "gap": 1, "english": 3}.get(role, rng.randint(0, 9))
            atts = sim.run_session(student, subj, rng, practice_steps=steps)
            st["subjects"][subj] = (atts, base + timedelta(minutes=rng.randint(0, 600)))
        out.append(st)
    return out


def populate(db, school, branch, tn, sn, built):
    """One branch's classroom: 2 teachers (6 classes) and the 18 students from build_class.
    tn / sn = how many teachers / students exist already, so ID codes stay unique. Returns the new counts."""
    t1 = _user(db, f"T{10000 + tn}", "teacher", "Ms. Lakshmi", school, branch, phone=str(9000000000 + tn))
    t2 = _user(db, f"T{10001 + tn}", "teacher", "Mr. Rahim", school, branch, phone=str(9000000001 + tn))
    asg = {}
    for t, subj, sec in [(t1, "maths", "A"), (t1, "maths", "B"), (t1, "physical", "A"),
                         (t2, "biology", "A"), (t2, "biology", "B"), (t2, "physical", "B")]:
        a = D.TeachingAssignment(teacher_id=t.id, branch_id=branch.id, subject=subj, class_no=8, section=sec)
        a.progress = json.dumps({"book": cat.BOOK, "year_status": "ongoing", "chapters_done": [],
                                 "current_chapter": cat.DEMO_CHAPTER[subj], "topic_reached": cat.SUBTOPICS[subj][1]})
        db.add(a)
        db.flush()
        asg[(subj, sec)] = a
    k = sn
    for st in built:
        k += 1
        s = _user(db, f"S{10000 + k}", "student", st["name"], school, branch, roll_no=st["roll"], class_no=8, section=st["sec"],
                  gender=st["gender"], board="telangana", state="telangana", area_type=st["area"], locality="Town", demo_role=st["role"])
        prog = {}
        for subj, (atts, t0) in st["subjects"].items():
            db.add(D.Enrollment(student_id=s.id, assignment_id=asg[(subj, st["sec"])].id, subject=subj, status="approved"))
            prog[subj] = {"book": cat.BOOK, "year_status": "ongoing", "chapters_done": [], "current_chapter": cat.DEMO_CHAPTER[subj],
                          "topic_reached": cat.SUBTOPICS[subj][0]}
            for i, a in enumerate(atts):
                db.add(D.Attempt(student_id=s.id, subject=subj, question_id=a["question_id"], concept=a["concept"],
                                 difficulty=a["difficulty"], load=a["load"], pair=a["pair"], chosen=_chosen(a), correct=a["correct"],
                                 tag=a["tag"], time_ms=a["time_ms"], hint=a["hint"], support=a["support"], mode=a["mode"],
                                 created=t0 + timedelta(seconds=40 * i)))
        s.progress = json.dumps(prog)
    return tn + 2, k


def seed(db):
    rng = random.Random(42)
    demo = D.School(name="Sunrise High School", teacher_code=SCHOOL_CODE)
    other = D.School(name="Lakeview Public School", teacher_code=SECOND_CODE)
    db.add_all([demo, other])
    db.flush()
    main = D.Branch(school_id=demo.id, name="Main Branch")
    east = D.Branch(school_id=demo.id, name="East Branch")
    only = D.Branch(school_id=other.id, name="Main Branch")
    db.add_all([main, east, only])
    db.flush()

    branches_all = [(demo, main), (demo, east), (other, only)]
    # Extra schools so the typed school search has real choices. Branch names are common Hyderabad localities,
    # not verified against each school's real branch list. Codes are invented for this project.
    for nm, code, branches in SCHOOLS:
        sc = D.School(name=nm, teacher_code=code)
        db.add(sc)
        db.flush()
        bs = [D.Branch(school_id=sc.id, name=b) for b in branches]
        db.add_all(bs)
        db.flush()
        branches_all += [(sc, x) for x in bs]

    built = build_class(rng)
    tn, sn = 1, 0
    for sc, br in branches_all:                 # every branch of every school gets the same synthetic classroom
        tn, sn = populate(db, sc, br, tn, sn, built)
    db.commit()


def _chosen(a):
    # the engine does not need the chosen index back, only that it is stored; keep it deterministic
    from . import bank
    q = bank.BY_ID[a["question_id"]]
    if a["correct"]:
        return q["answer"]
    for i in range(4):
        if i != q["answer"] and (a["tag"] is None or q["tags"].get(str(i)) == a["tag"]):
            return i
    return (q["answer"] + 1) % 4


def reset():
    _pin_cache.clear()
    D.Base.metadata.drop_all(D.engine)
    D.init()
    run_if_empty()
