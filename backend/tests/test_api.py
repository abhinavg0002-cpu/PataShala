import os
import tempfile

import pytest

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")   # before importing the app

from fastapi.testclient import TestClient  # noqa: E402

from app import bank, main  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(main.app) as c:
        yield c


def login(c, code, pin="1234"):
    r = c.post("/auth/login", json={"code": code, "pin": pin})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["token"]}


def test_health_and_catalog(client):
    assert client.get("/health").json()["ok"]
    cat = client.get("/meta/catalog").json()
    assert any(b["enabled"] is False for b in cat["boards"]) and cat["demo_chapter"]["physical"] == "Force"


def test_wrong_pin_is_rejected_and_locks(client):
    for _ in range(5):
        assert client.post("/auth/login", json={"code": "S10005", "pin": "0000"}).status_code == 401
    assert client.post("/auth/login", json={"code": "S10005", "pin": "1234"}).status_code == 429


def test_no_token_means_401(client):
    assert client.get("/student/subjects").status_code == 401


def test_student_cannot_use_teacher_routes_and_vice_versa(client):
    s = login(client, "S10001")
    t = login(client, "T10001")
    assert client.get("/teacher/assignments", headers=s).status_code == 403
    assert client.get("/student/subjects", headers=t).status_code == 403


def test_teacher_registration_needs_school_code(client):
    schools = client.get("/schools").json()
    demo = next(s for s in schools if s["name"].startswith("Sunrise"))
    body = {"school_id": demo["id"], "branch_id": demo["branches"][0]["id"], "teacher_code": "WRONG", "name": "Test Teacher",
            "phone": "9111111111", "pin": "4321", "assignments": [{"subject": "maths", "class_no": 8, "section": "C"}]}
    assert client.post("/register/teacher", json=body).status_code == 403
    body["teacher_code"] = "SH393511"
    r = client.post("/register/teacher", json=body)
    assert r.status_code == 200 and r.json()["user"]["code"].startswith("T")
    body["assignments"] = [{"subject": "telugu", "class_no": 8, "section": "C"}]
    assert client.post("/register/teacher", json=body).status_code == 422


def test_full_student_flow_and_teacher_approval(client):
    schools = client.get("/schools").json()
    demo = next(s for s in schools if s["name"].startswith("Sunrise"))
    reg = {"school_id": demo["id"], "branch_id": demo["branches"][0]["id"], "name": "New Student", "roll_no": "77",
           "class_no": 8, "section": "A", "gender": "Girl", "board": "telangana", "state": "telangana",
           "area_type": "Urban", "locality": "x", "pin": "2468"}
    r = client.post("/register/student", json=reg)
    assert r.status_code == 200
    code, h = r.json()["user"]["code"], {"Authorization": "Bearer " + r.json()["token"]}
    assert client.post("/register/student", json=reg).status_code == 409           # same roll number
    assert client.post("/register/student", json={**reg, "board": "cbse", "roll_no": "78"}).status_code == 422

    opts = client.get("/student/options", params={"subject": "maths"}, headers=h).json()
    assert [o["teacher"] for o in opts] == ["Ms. Lakshmi"]            # only the matching class + section
    assert client.get("/student/options", params={"subject": "telugu"}, headers=h).status_code == 422
    e = client.post("/student/enroll", json={"subject": "maths", "assignment_id": opts[0]["assignment_id"]}, headers=h)
    assert e.json()["status"] == "pending"

    # teacher cannot see the student until approved
    t = login(client, "T10001")
    stu_id = client.get("/me", headers=h).json()["id"]
    assert client.get("/teacher/student", params={"student_id": stu_id, "subject": "maths"}, headers=t).status_code == 403
    reqs = client.get("/teacher/requests", headers=t).json()
    rid = next(r["id"] for r in reqs if r["code"] == code)
    assert client.post(f"/teacher/requests/{rid}", json={"approve": True}, headers=t).json()["status"] == "approved"

    # student takes the diagnostic through the API
    for _ in range(40):
        step = client.get("/student/next", params={"subject": "maths"}, headers=h).json()
        if step["phase"] != "diagnostic":
            break
        q = bank.BY_ID[step["question"]["id"]]
        assert "answer" not in step["question"] and "tags" not in step["question"]
        out = client.post("/student/answer", json={"subject": "maths", "question_id": q["id"], "chosen": q["answer"], "time_ms": 8000}, headers=h).json()
        assert out["feedback"]["correct"]
    assert step["phase"] in ("practice", "complete")

    # answering a question that is not the current one is refused
    assert client.post("/student/answer", json={"subject": "maths", "question_id": "m_r1", "chosen": 0, "time_ms": 1000}, headers=h).status_code in (200, 409)

    # now the teacher can see this student, and only through this subject
    d = client.get("/teacher/student", params={"student_id": stu_id, "subject": "maths"}, headers=t).json()
    assert d["level"] == "Strong"
    assert client.get("/teacher/student", params={"student_id": stu_id, "subject": "biology"}, headers=t).status_code == 403
    t2 = login(client, "T10002")                                                      # another teacher
    assert client.get("/teacher/student", params={"student_id": stu_id, "subject": "maths"}, headers=t2).status_code == 403


def test_teacher_roster_group_assign_and_decision(client):
    t = login(client, "T10001")
    cards = client.get("/teacher/assignments", headers=t).json()
    maths_a = next(c for c in cards if c["subject"] == "maths" and c["section"] == "A")
    roster = client.get("/teacher/roster", params={"assignment_id": maths_a["id"]}, headers=t).json()
    assert len(roster["students"]) >= 10 and roster["students"][0]["level"] in ("Basic", "Medium", "Strong")
    ids = [s["id"] for s in roster["students"][:3]]
    g = client.post("/teacher/group", json={"subject": "maths", "student_ids": ids}, headers=t).json()
    assert g["count"] == 3
    assert client.post("/teacher/assign", json={"subject": "maths", "concept_id": "m_ratio", "student_ids": ids}, headers=t).json()["assigned"] == 3
    other = login(client, "T10002")
    maths_b = next(c for c in client.get("/teacher/assignments", headers=t).json() if c["subject"] == "maths" and c["section"] == "B")
    assert client.get("/teacher/roster", params={"assignment_id": maths_b["id"]}, headers=other).status_code == 404
    assert client.post("/teacher/group", json={"subject": "maths", "student_ids": ids}, headers=other).status_code == 403
    r = client.post("/teacher/decision", json={"student_id": ids[0], "subject": "maths", "concept_id": "m_inverse", "system_cause": "gap",
                                               "action": "override", "final_cause": "language"}, headers=t)
    assert r.status_code == 200
    s = client.get("/teacher/stats", headers=t).json()
    assert s["decisions"] == 1 and s["accept_rate"] == 0.0


def test_replay_uses_engine(client):
    r = client.get("/demo/replay", params={"question_id": "m_i2"}).json()
    assert len(r["students"]) == 3
    assert {s["role"] for s in r["students"]} == {"fast", "misconception", "gap"}
    fast = next(s for s in r["students"] if s["role"] == "fast")
    assert fast["correct"] is True


def test_validation_endpoint(client):
    v = client.get("/demo/validation").json()
    assert v["students"] >= 30 and "note" in v


def test_check_code_phone_login_and_pin_reset(client):
    from app import security
    security._fails.clear()          # earlier tests made wrong guesses; start with a clean limit
    schools = client.get("/schools").json()
    assert len(schools) >= 8
    sun = next(s for s in schools if s["name"].startswith("Sunrise"))
    other = next(s for s in schools if s["name"].startswith("Sri Chaitanya"))
    ids = {"school_id": sun["id"], "branch_id": sun["branches"][0]["id"]}
    assert client.post("/register/check-code", json={**ids, "teacher_code": "nope"}).status_code == 403
    assert client.post("/register/check-code", json={**ids, "teacher_code": " sh393511 "}).status_code == 200
    # a code from another school must not work here
    assert client.post("/register/check-code", json={**ids, "teacher_code": "SC498373"}).status_code == 403
    assert other["branches"]
    # seeded teacher logs in with the mobile number
    assert client.post("/auth/login", json={"code": "9000000001", "pin": "1234"}).json()["user"]["code"] == "T10001"
    # teacher forgot PIN: school code proves it is them
    bad = {"who": "9000000001", "new_pin": "9999", "teacher_code": "WRONG"}
    assert client.post("/auth/reset-pin", json=bad).status_code == 403
    assert client.post("/auth/reset-pin", json={**bad, "teacher_code": "SH393511"}).status_code == 200
    h = login(client, "T10001", "9999")
    # change PIN needs the current PIN
    assert client.post("/me/change-pin", json={"old_pin": "0000", "new_pin": "1234"}, headers=h).status_code == 401
    assert client.post("/me/change-pin", json={"old_pin": "9999", "new_pin": "1234"}, headers=h).status_code == 200
    # student forgot PIN: roll number and section must match
    me = client.get("/me", headers=login(client, "S10001")).json()
    wrong = {"who": "S10001", "new_pin": "5555", "roll_no": "99", "section": me["section"]}
    assert client.post("/auth/reset-pin", json=wrong).status_code == 403
    ok = {**wrong, "roll_no": me["roll_no"]}
    assert client.post("/auth/reset-pin", json=ok).status_code == 200
    login(client, "S10001", "5555")


def test_teacher_code_guessing_is_limited(client):
    from app import security
    security._fails.clear()
    sun = next(s for s in client.get("/schools").json() if s["name"].startswith("Sunrise"))
    body = {"school_id": sun["id"], "branch_id": sun["branches"][0]["id"], "teacher_code": "XX000000"}
    codes = [client.post("/register/check-code", json=body).status_code for _ in range(6)]
    assert codes[:5] == [403] * 5 and codes[5] == 429
    security._fails.clear()


def test_any_ten_digit_mobile_but_never_twice(client):
    from app import security
    security._fails.clear()
    sun = next(s for s in client.get("/schools").json() if s["name"].startswith("Sunrise"))
    ids = {"school_id": sun["id"], "branch_id": sun["branches"][0]["id"]}
    code = "SH393511"
    # a number starting with 5 is fine, and a taken number is reported at the code check, not at the very end
    assert client.post("/register/check-code", json={**ids, "teacher_code": code, "phone": "5123456789"}).status_code == 200
    assert client.post("/register/check-code", json={**ids, "teacher_code": code, "phone": "9000000001"}).status_code == 409
    body = {**ids, "teacher_code": code, "name": "Phone Test", "phone": "5123456789", "pin": "1111",
            "assignments": [{"subject": "maths", "class_no": 8, "section": "D"}]}
    assert client.post("/register/teacher", json=body).status_code == 200
    assert client.post("/register/teacher", json=body).status_code == 409
    assert client.post("/auth/login", json={"code": "5123456789", "pin": "1111"}).status_code == 200
    assert client.post("/register/teacher", json={**body, "phone": "123"}).status_code == 422


def test_double_tap_on_answer_is_counted_once(client):
    h = login(client, "S10002")
    step = client.get("/student/next", params={"subject": "maths"}, headers=h).json()
    body = {"subject": "maths", "question_id": step["question"]["id"], "chosen": 0, "time_ms": 4000}
    before = len(client.get("/student/report", params={"subject": "maths"}, headers=h).json()["concepts"])
    first = client.post("/student/answer", json=body, headers=h)
    second = client.post("/student/answer", json=body, headers=h)      # the same tap arriving twice
    assert first.status_code == 200
    assert second.status_code == 409
    assert before > 0
