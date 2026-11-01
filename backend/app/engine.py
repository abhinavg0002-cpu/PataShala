"""Adaptive engine: rule-based, explainable, no machine learning. Pure functions, no database.

An attempt is a dict:
  question_id, concept, difficulty (easy|medium|hard), load (low|high), pair, correct (bool),
  tag (misconception tag or None), time_ms, hint (0-3), support (None|simplified|example|recap),
  mode (diagnostic|practice)
Attempts are passed OLDEST FIRST. Thresholds below are STARTING VALUES, not validated (see Rules.md).
"""
from collections import Counter

from . import bank, catalog as cat

WEIGHT = {"easy": 1.0, "medium": 1.5, "hard": 2.0}
SECURE, DEVELOPING = 0.75, 0.45          # score cut-offs (Rules.md B1)
FAST_MS = 3000                           # wrong this fast = possible slip/guess (R10)
WINDOW = 6                               # last N attempts per concept
LANG_PAIRS_NEEDED = 2                    # R8: pairs showing "short right, word wrong"
ORDER = ["easy", "medium", "hard"]
CAUSE_ORDER = ["language", "prerequisite", "misconception", "gap", "slip"]


def credit(a):
    if not a["correct"]:
        return 0.0
    return 1.0 if a["hint"] == 0 else 0.5


def weighted(atts):
    den = sum(WEIGHT[a["difficulty"]] for a in atts)
    return None if den == 0 else sum(WEIGHT[a["difficulty"]] * credit(a) for a in atts) / den


def concept_status(atts_c):
    n = len(atts_c)
    if n == 0:
        return {"status": "no_evidence", "score": None, "n": 0, "weak_probe": False}
    last = atts_c[-WINDOW:]
    sc = weighted(last)
    weak_probe = n == 1 and not atts_c[0]["correct"]
    if n < 2:
        st = "no_evidence"
    elif sc >= SECURE and any(a["correct"] and a["hint"] == 0 and a["difficulty"] != "easy" for a in last):
        st = "secure"
    elif sc >= DEVELOPING:
        st = "developing"
    else:
        st = "needs_support"
    return {"status": st, "score": round(sc, 2), "n": n, "weak_probe": weak_probe}


def level_from_score(sc):
    if sc is None:
        return None
    return "Basic" if sc < DEVELOPING else ("Medium" if sc < SECURE else "Strong")


# ------------------------------------------------------------------ helpers
def _name(cid):
    return cat.CONCEPT[cid]["name"]


def _by_concept(atts):
    d = {}
    for a in atts:
        d.setdefault(a["concept"], []).append(a)
    return d


def _first(concept, diff=None, load=None, pair=None, exclude=()):
    for q in bank.questions_for(concept):
        if diff and q["difficulty"] != diff:
            continue
        if load and q["load"] != load:
            continue
        if pair and q["pair"] != pair:
            continue
        if q["id"] in exclude:
            continue
        return q
    return None


def _trace(rule, headline, observed, decision, student, teacher=None):
    return {"rule": rule, "headline": headline, "observed": observed, "decision": decision,
            "student_text": student, "teacher_text": teacher or student}


def _prereqs(cid):
    out, todo = set(), list(cat.CONCEPT[cid]["prereq"])
    while todo:
        p = todo.pop()
        if p not in out:
            out.add(p)
            todo += cat.CONCEPT[p]["prereq"]
    return out


def _mark(a):
    return "right" if a["correct"] else "wrong"


# ------------------------------------------------------------------ likely causes
def language_pairs(atts):
    """Pairs where the short (low-load) version was right and the word (high-load) version wrong."""
    latest = {}
    for a in atts:
        if a["pair"]:
            latest.setdefault(a["pair"], {})[a["load"]] = a
    both = {p: v for p, v in latest.items() if "low" in v and "high" in v}
    hit = [p for p, v in both.items() if v["low"]["correct"] and not v["high"]["correct"]]
    return {"pairs_tested": len(both), "pairs_hit": hit}


def concept_causes(atts, cid, statuses, lang):
    ca = [a for a in atts if a["concept"] == cid]
    st = statuses[cid]
    if st["status"] in ("secure", "no_evidence") and not st["weak_probe"]:
        return []
    wrong = [a for a in ca if not a["correct"]]
    out = []
    tags = Counter(a["tag"] for a in wrong if a["tag"])
    for tag, n in tags.most_common():
        if n >= 2 and n / len(wrong) >= 0.6:          # most wrong answers share one wrong idea
            out.append({"type": "misconception", "tag": tag, "label": cat.TAGS[tag][0], "rule": "R7",
                        "evidence": [f"Chose the same kind of wrong answer {n} times: {cat.TAGS[tag][0].lower()}."]})
            break
    pairs = {}
    for a in ca:
        if a["pair"]:
            pairs.setdefault(a["pair"], {})[a["load"]] = a
    pat = [p for p, v in pairs.items() if "low" in v and "high" in v and v["low"]["correct"] and not v["high"]["correct"]]
    if pat and len(lang["pairs_hit"]) >= LANG_PAIRS_NEEDED:
        out.append({"type": "language", "rule": "R8", "label": "English / reading load",
                    "evidence": [f"Short version right, word version wrong in {len(lang['pairs_hit'])} of {lang['pairs_tested']} paired questions across this subject."]})
    weak_pre = [p for p in cat.CONCEPT[cid]["prereq"]
                if statuses[p]["status"] == "needs_support" or statuses[p]["weak_probe"]]
    if weak_pre and st["status"] != "secure":
        out.append({"type": "prerequisite", "rule": "R6", "label": "Missing earlier skill",
                    "prereq": weak_pre[0],
                    "evidence": [f"{_name(weak_pre[0])} (needed first) is also weak."]})
    low_wrong = [a for a in wrong if a["load"] == "low"]
    if st["status"] == "needs_support" and low_wrong and not any(o["type"] == "misconception" for o in out):
        out.append({"type": "gap", "rule": "R9", "label": "Concept gap",
                    "evidence": ["Wrong even on the short / easier version of the question."]})
    if wrong and all(a["time_ms"] < FAST_MS for a in wrong) and len(wrong) <= 2:
        out.append({"type": "slip", "rule": "R10", "label": "Possible slip or guess",
                    "evidence": ["Wrong answers came very fast (under 3 seconds)."]})
    out.sort(key=lambda c: CAUSE_ORDER.index(c["type"]))
    return out


# ------------------------------------------------------------------ diagnostic (R1, R2, R3, R5, R8-check)
def diag_next(subject, atts):
    """Next diagnostic question, or None when the diagnostic is finished."""
    diag = [a for a in atts if a["mode"] == "diagnostic"]
    seen = {a["question_id"]: a for a in diag}
    for cid in cat.subject_main_concepts(subject):
        nm = _name(cid)
        mc = _first(cid, "medium", "low")
        if mc["id"] not in seen:
            return mc, _trace("R1", "Start with one medium question",
                              [f"Concept: {nm}", "No answers yet on this concept"],
                              "Ask one medium question to see where the student is.",
                              f"Let's see where you are with {nm}. Here is a medium question.")
        A = seen[mc["id"]]
        partner = _first(cid, "medium", "high", pair=mc["pair"])
        if partner and partner["id"] not in seen:
            return partner, _trace("R8", "Same skill in a word problem",
                                   [f"{nm}: short question was {_mark(A)}"],
                                   "Ask the same skill as a word problem, to tell a maths gap from an English problem.",
                                   "Now the same idea as a word problem.",
                                   "Paired question: same skill, longer English. Compares maths with reading load.")
        B = seen.get(partner["id"]) if partner else None
        if not A["correct"]:
            easy = _first(cid, "easy")
            if easy and easy["id"] not in seen:
                return easy, _trace("R3", "Wrong → check with an easier question",
                                    [f"{nm}: medium question was wrong"],
                                    "Ask an easy question to separate a real gap from a slip.",
                                    "That one was tricky. Let's try an easier one.")
            E = seen.get(easy["id"]) if easy else None
            if E is not None and not E["correct"]:
                for p in cat.CONCEPT[cid]["prereq"]:
                    if cat.CONCEPT[p]["main"]:
                        continue
                    probe = _first(p, "easy")
                    if probe and probe["id"] not in seen:
                        return probe, _trace("R5", "Easy also wrong → check the earlier skill",
                                             [f"{nm}: medium wrong, easy wrong"],
                                             f"Probe the prerequisite: {_name(p)}.",
                                             f"Let's check an earlier skill that {nm} needs: {_name(p)}.")
        elif B is not None and B["correct"]:
            hard = _first(cid, "hard")
            if hard and hard["id"] not in seen:
                return hard, _trace("R2", "Both medium versions right → try a hard question",
                                    [f"{nm}: medium short right, medium word right"],
                                    "Raise the difficulty to place the student's level.",
                                    "Great! Let's try a harder one.")
    return None, None


def diagnostic_progress(subject, atts):
    q, _ = diag_next(subject, atts)
    return q is None


# ------------------------------------------------------------------ analysis
def analyse(subject, atts):
    ids = cat.SUBJECT_CONCEPTS[subject]
    byc = _by_concept(atts)
    statuses = {cid: concept_status(byc.get(cid, [])) for cid in ids}
    lang = language_pairs(atts)
    lang_flag = len(lang["pairs_hit"]) >= LANG_PAIRS_NEEDED
    causes = {cid: concept_causes(atts, cid, statuses, lang) for cid in ids}
    done = diagnostic_progress(subject, atts)
    mains = set(cat.subject_main_concepts(subject))
    diag_main = [a for a in atts if a["mode"] == "diagnostic" and a["concept"] in mains]
    sc = weighted(diag_main)
    level = level_from_score(sc) if done else None
    flags = []
    for cid in ids:
        n3 = sum(1 for a in byc.get(cid, []) if a["hint"] == 3)
        if n3 >= 3:
            flags.append({"rule": "R11", "concept": cid, "text": f"Needed the biggest hint {n3} times on {_name(cid)}: needs teacher help."})
    helped = {}
    for a in atts:
        k = a["support"] or ("hint" if a["hint"] else None)
        if k:
            h = helped.setdefault(k, {"support": k, "tries": 0, "correct": 0})
            h["tries"] += 1
            h["correct"] += 1 if a["correct"] else 0
    weak = [cid for cid in ids if statuses[cid]["status"] == "needs_support" or statuses[cid]["weak_probe"]]
    strong = [cid for cid in ids if statuses[cid]["status"] == "secure"]
    counts = Counter(statuses[cid]["status"] for cid in ids if cat.CONCEPT[cid]["main"])
    return {"subject": subject, "diagnostic_done": done, "baseline_score": None if sc is None else round(sc, 2),
            "level": level, "statuses": statuses, "causes": causes, "language": {**lang, "flag": lang_flag},
            "flags": flags, "what_helped": list(helped.values()), "weak": weak, "strong": strong,
            "counts": {k: counts.get(k, 0) for k in ("needs_support", "developing", "secure", "no_evidence")},
            "answered": len(atts)}


# ------------------------------------------------------------------ practice (R2, R3, R4, R6, R8, R12)
def _pick_target(subject, an, assigned):
    st = an["statuses"]
    for cid in assigned:
        if cid in st:
            return cid, "teacher"
    ids = cat.SUBJECT_CONCEPTS[subject]
    for cid in ids:
        if st[cid]["status"] == "needs_support" or st[cid]["weak_probe"]:
            return cid, "weak"
    for cid in ids:
        if st[cid]["status"] == "developing":
            return cid, "developing"
    for cid in ids:
        if cat.CONCEPT[cid]["main"] and st[cid]["status"] == "no_evidence":
            return cid, "new"
    return None, "done"


def _choose_question(cid, diff, atts):
    seen_ids = [a["question_id"] for a in atts]
    qs = bank.questions_for(cid)
    order = sorted(ORDER, key=lambda d: abs(ORDER.index(d) - ORDER.index(diff)))
    for d in order:
        for q in qs:
            if q["difficulty"] == d and q["id"] not in seen_ids:
                return q
    # all seen: pick the least recently seen at the wanted level
    cand = [q for q in qs if q["difficulty"] == diff] or qs
    return min(cand, key=lambda q: max([i for i, s in enumerate(seen_ids) if s == q["id"]] or [-1]))


def _next_step(subject, atts, assigned=()):
    an = analyse(subject, atts)
    progress = {"answered": len(atts), "diagnostic_done": an["diagnostic_done"]}
    if not an["diagnostic_done"]:
        q, tr = diag_next(subject, atts)
        return {"phase": "diagnostic", "stage": "Diagnostic", "concept": q["concept"], "lesson": None,
                "question": bank.public_question(q), "support": None, "trace": tr, "progress": progress}
    cid, why = _pick_target(subject, an, assigned)
    if cid is None:
        seen_ids = {a["question_id"] for a in atts}
        hard = [q for c in cat.subject_main_concepts(subject) for q in bank.questions_for(c)
                if q["difficulty"] == "hard" and q["id"] not in seen_ids]
        if hard:
            q = hard[0]
            return {"phase": "practice", "stage": "Test", "concept": q["concept"], "lesson": None,
                    "question": bank.public_question(q), "support": None, "progress": progress,
                    "trace": _trace("R12", "All concepts secure → fast-track challenge",
                                    [f"{_name(c)} is Secure" for c in an["strong"] if cat.CONCEPT[c]["main"]],
                                    "Offer an unseen hard question instead of more of the same.",
                                    "You know this chapter well. Here is a challenge question!",
                                    "Fast track: every concept is Secure, so the student gets unseen hard questions.")}
        return {"phase": "complete", "stage": None, "concept": None, "lesson": None, "question": None,
                "support": None, "progress": progress,
                "trace": _trace("R12", "All concepts are secure",
                                [f"{_name(c)} is Secure" for c in an["strong"]],
                                "Nothing left to catch up on. Offer challenge questions.",
                                "You have mastered this chapter. Well done!",
                                "Every concept in this chapter is Secure. Fast-track challenge is available.")}
    st = an["statuses"][cid]
    nm = _name(cid)
    pa = [a for a in atts if a["concept"] == cid and a["mode"] == "practice"]
    last_prac = [a for a in atts if a["mode"] == "practice"]
    first_visit = not pa
    lang_flag = an["language"]["flag"]
    support = None
    lesson = None
    prev_concept = last_prac[-1]["concept"] if last_prac else None
    moved = prev_concept is not None and prev_concept != cid

    mis = next((c for c in an["causes"][cid] if c["type"] == "misconception"), None)
    if pa:
        last2 = pa[-2:]
        last = pa[-1]
        if mis and not last["correct"] and last["tag"] == mis["tag"]:
            diff = last["difficulty"]
            support = "contrast"
            lesson = cat.CONCEPT[cid]["learn"]
            tr = _trace("R7", "Same wrong idea again → contrast example",
                        [f"Chose the wrong idea '{mis['label']}' again on {nm}"],
                        "Show an example that tackles this exact mistake, then a question at the same level.",
                        "You made the same kind of mistake again. Let's look at why it does not work.",
                        f"Misconception '{mis['label']}' repeated (R7). Contrast example shown.")
        elif len(last2) == 2 and all(a["correct"] for a in last2):
            diff = ORDER[min(ORDER.index(last["difficulty"]) + 1, 2)]
            tr = _trace("R2", "Two correct in a row → harder question",
                        [f"Last 2 answers on {nm}: right, right"], f"Raise difficulty to {diff}.",
                        "You got two in a row. Let's try something harder.")
        elif len(last2) == 2 and not any(a["correct"] for a in last2):
            diff = ORDER[max(ORDER.index(last["difficulty"]) - 1, 0)]
            support = "example"
            lesson = cat.CONCEPT[cid]["learn"]
            tr = _trace("R4", "Two wrong in a row → easier step + worked example",
                        [f"Last 2 answers on {nm}: wrong, wrong"],
                        f"Lower difficulty to {diff} and show a worked example first.",
                        "Let's slow down. Here is a worked example, then an easier question.")
        elif not last["correct"]:
            diff = last["difficulty"]
            tr = _trace("R3", "One wrong → same level, new question, hint available",
                        [f"Last answer on {nm}: wrong"], "Stay at this level with a different question.",
                        "Not quite. Try a different question. You can use a hint.")
        else:
            diff = last["difficulty"]
            before = "only one answer so far" if len(pa) == 1 else "the one before was wrong"
            tr = _trace("R3", "Keep practising at this level",
                        [f"Last answer on {nm}: right ({before})"],
                        "Stay at this level for one more to confirm.", "Good. One more at this level.")
    else:
        diff = {"needs_support": "easy", "developing": "medium", "secure": "hard", "no_evidence": "medium"}[st["status"]]
        if st["weak_probe"]:
            diff = "easy"
        lesson = cat.CONCEPT[cid]["learn"]
        if why == "teacher":
            tr = _trace("R-T", "Your teacher assigned this concept", [f"Teacher asked for practice on {nm}"],
                        f"Learn {nm}, then practise at {diff} level.", f"Your teacher asked you to practise {nm}.")
        elif cat.CONCEPT[cid]["main"] is False:
            tr = _trace("R6", "Earlier skill is weak → go back to it first",
                        [f"{nm} is weak (from the diagnostic)"],
                        f"Recap {nm} before returning to the chapter.",
                        f"We will first brush up an earlier skill: {nm}.",
                        f"Prerequisite recap: {nm} was weak, so it comes before the chapter concepts.")
            support = "recap"
        else:
            ev = [f"{nm}: {st['status'].replace('_', ' ')} (score {st['score']})"] if st["score"] is not None else [f"{nm}: not enough evidence"]
            if moved and an["statuses"][prev_concept]["status"] == "secure":
                ev.insert(0, f"{_name(prev_concept)} is now Secure")
                tr = _trace("R12", "Concept secure → move to the next one", ev,
                            f"Move on to {nm} and start at {diff} level.", f"Well done! Next up: {nm}.")
            else:
                tr = _trace("R2", "Weakest concept first", ev, f"Learn {nm}, then start at {diff} level.",
                            f"Next we will work on {nm}.")
    if st["weak_probe"] and why != "teacher" and not cat.CONCEPT[cid]["main"]:
        support = "recap"
    if moved and why == "weak" and cid in _prereqs(prev_concept) and an["statuses"][prev_concept]["status"] != "secure":
        tr = _trace("R6", "Earlier skill is weak → go back to it first",
                    [f"Last answer was on {_name(prev_concept)}", f"{nm} (needed first) is still weak"] + tr["observed"],
                    f"Return to {nm} before continuing with {_name(prev_concept)}.",
                    f"Let's go back to an earlier skill first: {nm}.",
                    f"Prerequisite {nm} is weak, so the student is sent back to it (R6).")
        lesson = lesson or cat.CONCEPT[cid]["learn"]
    if lesson and mis:
        lesson = {**lesson, "contrast": {"label": mis["label"], "fix": cat.TAGS[mis["tag"]][1]}}
    q = _choose_question(cid, diff, atts)
    if lang_flag and q["load"] == "high" and q["simple"]:
        support = "simplified" if support is None else support
        tr["observed"].append("Word questions were missed while short ones were right (R8): showing plain wording.")
        tr["student_text"] += " The question uses simpler words."
        tr["teacher_text"] += " Served the plain-wording version (R8)."
    stage = "Test" if q["difficulty"] == "hard" else "Solve"
    if lesson:
        stage = "Learn"
    return {"phase": "practice", "stage": stage, "concept": cid, "lesson": lesson,
            "question": bank.public_question(q, simplified=(support == "simplified")),
            "support": support, "trace": tr, "progress": progress}


# ------------------------------------------------------------------ marking
def mark(question, chosen):
    correct = chosen == question["answer"]
    tag = None if correct else question["tags"].get(str(chosen))
    fix = cat.TAGS[tag][1] if tag else None
    return {"correct": correct, "tag": tag, "tag_label": cat.TAGS[tag][0] if tag else None, "fix": fix,
            "why": question["why"], "answer": question["answer"], "answer_text": question["options"][question["answer"]]}


def next_step(subject, atts, assigned=()):
    out = _next_step(subject, atts, assigned)
    out["concept_name"] = _name(out["concept"]) if out["concept"] else None
    return out
