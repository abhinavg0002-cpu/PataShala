import random

from app import bank, catalog as cat, engine, sim


def att(qid, correct=True, hint=0, ms=9000, mode="practice", support=None, chosen=None):
    q = bank.BY_ID[qid]
    tag = None
    if not correct and chosen is not None:
        tag = q["tags"].get(str(chosen))
    return {"question_id": qid, "concept": q["concept"], "difficulty": q["difficulty"], "load": q["load"],
            "pair": q["pair"], "correct": correct, "tag": tag, "time_ms": ms, "hint": hint,
            "support": support, "mode": mode}


# ---------------------------------------------------------------- data checks
def test_bank_is_consistent():
    for q in bank.BANK:
        assert q["concept"] in cat.CONCEPT, q["id"]
        assert q["options"][q["answer"]], q["id"]
        for idx, tag in q["tags"].items():
            assert int(idx) != q["answer"], (q["id"], "tag on the right answer")
            assert tag in cat.TAGS, (q["id"], tag)
        if q["load"] == "high" and q["difficulty"] != "easy":
            assert q["simple"], (q["id"], "high-load question needs plain wording")
    for cid in cat.SUBJECT_CONCEPTS["maths"] + cat.SUBJECT_CONCEPTS["physical"] + cat.SUBJECT_CONCEPTS["biology"]:
        qs = bank.questions_for(cid)
        assert any(q["difficulty"] == "easy" for q in qs), cid
        mc = [q for q in qs if q["difficulty"] == "medium" and q["load"] == "low" and q["pair"]]
        assert mc, cid
        assert any(q["pair"] == mc[0]["pair"] and q["load"] == "high" for q in qs), cid


def test_maths_answers_are_correct():
    # recompute the number answers independently
    checks = {"m_r2": 40 / 5, "m_r3": 90 / 6, "m_d2": 60 * 3 / 12, "m_d3": 40 * 2 / 8, "m_d4": 22 * 600 / 15,
              "m_d5": 7 * 180 / 4, "m_i2": 6 * 12 / 9, "m_i3": 4 * 18 / 6, "m_i4": 48 * 5 / 4, "m_i5": 80 * 30 / 100,
              "m_c2": 6 * 8 * 10 / (4 * 6), "m_c3": 12 * 6 * 15 / (18 * 5), "m_c4": 600 * (100 / 150) * (15 / 20),
              "p_m2": 40 / 2, "p_m3": 30 / 2, "p_n2": 10 - 4, "p_n3": 30 - 20, "p_n4": 12 + 7 - 15, "p_p2": 100 / 4, "p_p3": 60 / 3,
              "b_s3": 90 * 10}
    for qid, want in checks.items():
        q = bank.BY_ID[qid]
        got = q["options"][q["answer"]].replace(",", "")
        num = float("".join(ch for ch in got.split()[0] if ch.isdigit() or ch == "."))
        assert abs(num - want) < 1e-6, (qid, num, want)


# ---------------------------------------------------------------- status and level
def test_status_needs_two_attempts():
    assert engine.concept_status([att("m_i2")])["status"] == "no_evidence"


def test_secure_needs_a_medium_or_hard_without_hint():
    a = [att("m_i1"), att("m_i1", hint=0)]
    assert engine.concept_status(a)["status"] == "developing"           # easy only
    b = a + [att("m_i2")]
    assert engine.concept_status(b)["status"] == "secure"


def test_hint_counts_half():
    s = engine.concept_status([att("m_i2", hint=1), att("m_i3", hint=1)])
    assert s["score"] == 0.5


def test_needs_support_when_wrong():
    s = engine.concept_status([att("m_i2", False), att("m_i3", False)])
    assert s["status"] == "needs_support"


def test_level_thresholds():
    assert engine.level_from_score(0.3) == "Basic"
    assert engine.level_from_score(0.6) == "Medium"
    assert engine.level_from_score(0.9) == "Strong"


# ---------------------------------------------------------------- diagnostic flow
def test_diagnostic_starts_with_medium_short():
    n = engine.next_step("maths", [])
    assert n["phase"] == "diagnostic" and n["question"]["id"] == "m_d2" and n["trace"]["rule"] == "R1"
    assert "answer" not in n["question"] and "tags" not in n["question"]


def test_wrong_medium_leads_to_pair_then_easy_then_prereq_probe():
    a = [att("m_d2", False, mode="diagnostic")]
    assert engine.next_step("maths", a)["question"]["id"] == "m_d3"          # word version
    a.append(att("m_d3", False, mode="diagnostic"))
    assert engine.next_step("maths", a)["question"]["id"] == "m_d1"          # easy
    a.append(att("m_d1", False, mode="diagnostic"))
    n = engine.next_step("maths", a)
    assert n["question"]["id"] == "m_r1" and n["trace"]["rule"] == "R5"       # prerequisite probe


def test_both_right_goes_to_hard():
    a = [att("m_d2", mode="diagnostic"), att("m_d3", mode="diagnostic")]
    n = engine.next_step("maths", a)
    assert n["question"]["id"] == "m_d4" and n["trace"]["rule"] == "R2"


def test_short_right_word_wrong_does_not_ask_hard():
    a = [att("m_d2", mode="diagnostic"), att("m_d3", False, mode="diagnostic")]
    n = engine.next_step("maths", a)
    assert n["question"]["concept"] == "m_inverse"                            # moved on


# ---------------------------------------------------------------- likely cause
def _lang_student():
    """Right on short, wrong on word problems in 2 concepts."""
    a = []
    for c in ("b_discovery", "b_parts"):
        mc = engine._first(c, "medium", "low")
        pt = engine._first(c, "medium", "high")
        a += [att(mc["id"], True, mode="diagnostic"), att(pt["id"], False, mode="diagnostic")]
    return a


def test_english_load_flagged_after_two_pairs():
    an = engine.analyse("biology", _lang_student())
    assert an["language"]["flag"] is True
    types = [c["type"] for c in an["causes"]["b_parts"]]
    assert "language" in types


def test_one_pair_is_not_enough_for_english_flag():
    a = _lang_student()[:2]
    assert engine.analyse("biology", a)["language"]["flag"] is False


def test_misconception_needs_same_tag_twice():
    one = [att("m_i2", False, chosen=1), att("m_i3", False, chosen=2)]
    assert not any(c["type"] == "misconception" for c in engine.analyse("maths", one)["causes"]["m_inverse"])
    two = [att("m_i2", False, chosen=1), att("m_i3", False, chosen=1)]
    cs = engine.analyse("maths", two)["causes"]["m_inverse"]
    assert cs[0]["type"] == "misconception" and cs[0]["tag"] == "treats_inverse_as_direct"


def test_prerequisite_cause():
    a = [att("m_r1", False, mode="diagnostic"), att("m_r2", False), att("m_i2", False), att("m_i3", False)]
    types = [c["type"] for c in engine.analyse("maths", a)["causes"]["m_inverse"]]
    assert "prerequisite" in types


def test_slip_when_wrong_answers_are_fast():
    a = [att("m_i2", False, ms=1500), att("m_i3", True)]
    a += [att("m_i4", False, ms=1800), att("m_i1", True)]
    an = engine.analyse("maths", a)
    assert any(c["type"] == "slip" for c in an["causes"]["m_inverse"]) or an["statuses"]["m_inverse"]["status"] == "secure"


# ---------------------------------------------------------------- practice rules
def _finished_diag(subject="maths"):
    rng = random.Random(1)
    s = sim.SimStudent(knows={c: False for c in cat.SUBJECT_CONCEPTS[subject]})
    return sim.run_session(s, subject, rng)


def test_practice_targets_prerequisite_first():
    a = _finished_diag()
    n = engine.next_step("maths", a)
    assert n["phase"] == "practice" and n["concept"] == "m_ratio" and n["lesson"] is not None
    assert n["trace"]["rule"] == "R6"


def test_two_wrong_in_practice_steps_down_with_example():
    a = _finished_diag()
    n = engine.next_step("maths", a)
    a.append(att(n["question"]["id"], False))
    n = engine.next_step("maths", a)
    a.append(att(n["question"]["id"], False))
    n = engine.next_step("maths", a)
    assert n["trace"]["rule"] == "R4" and n["support"] == "example" and n["lesson"]


def test_two_right_steps_up():
    a = _finished_diag()
    a += [att("m_r1", True), att("m_r2", True)]        # two practice answers right on the same concept
    n = engine.next_step("maths", a, assigned=["m_ratio"])
    assert n["trace"]["rule"] == "R2" and n["question"]["difficulty"] == "hard"


def test_assigned_concept_is_served_first():
    rng = random.Random(3)
    s = sim.SimStudent(knows={c: True for c in cat.SUBJECT_CONCEPTS["maths"]})
    a = sim.run_session(s, "maths", rng)
    n = engine.next_step("maths", a, assigned=["m_compound"])
    assert n["concept"] == "m_compound" and n["trace"]["rule"] == "R-T"


def test_language_flag_serves_plain_wording():
    a = _lang_student()
    # finish the biology diagnostic quickly with correct answers on the rest
    for _ in range(40):
        n = engine.next_step("biology", a)
        if n["phase"] != "diagnostic":
            break
        a.append(att(n["question"]["id"], True, mode="diagnostic"))
    n = engine.next_step("biology", a)
    if n["phase"] == "practice" and bank.BY_ID[n["question"]["id"]]["load"] == "high":
        assert n["support"] == "simplified"


def test_mark_returns_fix_for_tagged_wrong_option():
    q = bank.BY_ID["m_i2"]
    r = engine.mark(q, 1)
    assert not r["correct"] and r["tag"] == "treats_inverse_as_direct" and r["fix"]
    assert engine.mark(q, q["answer"])["correct"]


def test_simulation_runs_and_is_deterministic():
    r1 = sim.validate(n=30, seed=7)
    r2 = sim.validate(n=30, seed=7)
    assert r1 == r2 and r1["students"] == 30
