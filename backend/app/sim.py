"""Synthetic students: used to seed the demo and to run the validation simulation.

A SimStudent has HIDDEN truth (which concepts they really know, how much English hurts, which
wrong idea they hold). The engine never sees this; it only sees the answers. Comparing the engine's
output with the hidden truth is the validation. These are invented behaviours, so results show how
the rules behave on our assumptions, NOT how real students behave.
"""
import random
from dataclasses import dataclass, field

from . import bank, catalog as cat, engine


@dataclass
class SimStudent:
    knows: dict = field(default_factory=dict)         # concept -> bool
    lang_penalty: float = 0.0                         # 0..1 chance English breaks a word problem
    misconception: dict = field(default_factory=dict)  # concept -> tag held when not knowing
    slip: float = 0.04
    guess: float = 0.2


def _attempt(q, chosen, time_ms, hint, support, mode):
    return {"question_id": q["id"], "concept": q["concept"], "difficulty": q["difficulty"], "load": q["load"],
            "pair": q["pair"], "correct": chosen == q["answer"], "tag": q["tags"].get(str(chosen)) if chosen != q["answer"] else None,
            "time_ms": time_ms, "hint": hint, "support": support, "mode": mode}


def answer(sim, q, rng, simplified=False):
    """Return (chosen_option, time_ms)."""
    knows = sim.knows.get(q["concept"], False)
    penalty = sim.lang_penalty * (0.15 if simplified else 1.0) if q["load"] == "high" else 0.0
    if knows:
        p_right = (1 - sim.slip) * (1 - penalty) + penalty * sim.guess
    else:
        p_right = sim.guess * 0.5
    if rng.random() < p_right:
        return q["answer"], rng.randint(7000, 20000)
    wrong = [i for i in range(4) if i != q["answer"]]
    held = sim.misconception.get(q["concept"])
    if not knows and held:
        match = [i for i in wrong if q["tags"].get(str(i)) == held]
        if match and rng.random() < 0.85:
            return rng.choice(match), rng.randint(6000, 15000)
    fast = knows and rng.random() < 0.5      # a slip by a student who knows it is often quick
    return rng.choice(wrong), rng.randint(1200, 2800) if fast else rng.randint(5000, 16000)


def run_session(sim, subject, rng, practice_steps=0, learn_rate=0.3):
    """Take the diagnostic, then optional practice. Returns the attempt list (oldest first)."""
    atts = []
    for _ in range(60):                                   # hard stop: no infinite loops
        step = engine.next_step(subject, atts)
        if step["phase"] != "diagnostic":
            break
        q = bank.BY_ID[step["question"]["id"]]
        ch, ms = answer(sim, q, rng)
        atts.append(_attempt(q, ch, ms, 0, None, "diagnostic"))
    for _ in range(practice_steps):
        step = engine.next_step(subject, atts)
        if step["phase"] != "practice":
            break
        q = bank.BY_ID[step["question"]["id"]]
        simp = step["support"] == "simplified"
        ch, ms = answer(sim, q, rng, simplified=simp)
        atts.append(_attempt(q, ch, ms, 0, step["support"], "practice"))
        c = q["concept"]
        if not sim.knows.get(c) and (step["lesson"] or step["support"]) and rng.random() < learn_rate:
            sim.knows[c] = True                           # assumption: lessons/examples help some
    return atts


# ---------------------------------------------------------------- validation simulation
def fixed_test(subject):
    """A plain fixed 10-question test (every concept's medium short question, then hard ones)."""
    qs = [_q for c in cat.SUBJECT_CONCEPTS[subject] for _q in bank.questions_for(c) if _q["difficulty"] == "medium" and _q["load"] == "low"]
    qs += [_q for c in cat.SUBJECT_CONCEPTS[subject] for _q in bank.questions_for(c) if _q["difficulty"] == "hard"]
    return qs[:10]


def random_hidden(subject, rng):
    mains = cat.subject_main_concepts(subject)
    kind = rng.choice(["gap", "prereq", "misconception", "language", "strong"])
    sim = SimStudent(knows={c: True for c in cat.SUBJECT_CONCEPTS[subject]})
    weak = []
    if kind == "gap":
        weak = rng.sample(mains, rng.randint(1, 2))
    elif kind == "prereq":
        pre = [c for c in cat.SUBJECT_CONCEPTS[subject] if not cat.CONCEPT[c]["main"]][0]
        sim.knows[pre] = False
        weak = [c for c in mains if pre in cat.CONCEPT[c]["prereq"]][:2] or mains[:1]
    elif kind == "misconception":
        weak = [rng.choice(mains)]
        tags = {t for q in bank.questions_for(weak[0]) for t in q["tags"].values()}
        sim.misconception[weak[0]] = rng.choice(sorted(tags))
    elif kind == "language":
        sim.lang_penalty = 0.9
    for c in weak:
        sim.knows[c] = False
    return sim, kind, weak


def validate(n=50, seed=2026):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        subject = rng.choice(["maths", "physical", "biology"])
        sim, kind, weak = random_hidden(subject, rng)
        atts = run_session(sim, subject, rng)
        an = engine.analyse(subject, atts)
        mains = cat.subject_main_concepts(subject)
        flagged = {c for c in mains if an["statuses"][c]["status"] in ("needs_support", "developing") or an["statuses"][c]["weak_probe"]}
        # baseline: fixed 10-question test; a concept is "weak" if it has a wrong answer and no right one
        ft = fixed_test(subject)
        res = {}
        for q in ft:
            ch, _ = answer(sim, q, rng)
            res.setdefault(q["concept"], []).append(ch == q["answer"])
        base = {c for c in mains if c in res and not any(res[c])}
        engine_causes = {c: [x["type"] for x in an["causes"][c]] for c in mains}
        primary = {c: v[0] for c, v in engine_causes.items() if v}
        rows.append({"kind": kind, "weak": weak, "engine": sorted(flagged), "fixed": sorted(base),
                     "primary": primary, "language_flag": an["language"]["flag"], "n_diag": len(atts)})

    def prf(key, kinds):
        tp = fp = fn = 0
        for r in rows:
            if r["kind"] not in kinds:
                continue
            t, p = set(r["weak"]), set(r[key])
            tp += len(t & p); fp += len(p - t); fn += len(t - p)
        pr = tp / (tp + fp) if tp + fp else None
        rc = tp / (tp + fn) if tp + fn else None
        return {"precision": None if pr is None else round(pr, 2), "recall": None if rc is None else round(rc, 2)}

    weak_kinds = ("gap", "prereq", "misconception")
    lang_rows = [r for r in rows if r["kind"] == "language"]
    strong_rows = [r for r in rows if r["kind"] == "strong"]
    cause_rows = [r for r in rows if r["kind"] in ("gap", "prereq", "misconception")]

    def cause_hit(r):
        want = {"gap": {"gap", "prerequisite"}, "prereq": {"prerequisite", "gap"}, "misconception": {"misconception"}}[r["kind"]]
        return any(p in want for c, p in r["primary"].items() if c in r["weak"] or r["kind"] == "prereq")

    return {
        "note": "Synthetic students with invented behaviour. Shows how the rules behave on our assumptions, not on real students.",
        "students": n, "seed": seed,
        "weak_concepts_engine": prf("engine", weak_kinds),
        "weak_concepts_fixed10": prf("fixed", weak_kinds),
        "english_load": {"students": len(lang_rows),
                         "engine_flagged": sum(1 for r in lang_rows if r["language_flag"]),
                         "fixed10_can_flag": 0},
        "false_language_flags_on_other_students": sum(1 for r in rows if r["kind"] != "language" and r["language_flag"]),
        "strong_students": {"n": len(strong_rows),
                            "wrongly_flagged_weak": sum(1 for r in strong_rows if r["engine"])},
        "cause_primary_matches": {"n": len(cause_rows), "matched": sum(1 for r in cause_rows if cause_hit(r))},
        "avg_diagnostic_questions": round(sum(r["n_diag"] for r in rows) / len(rows), 1),
    }
