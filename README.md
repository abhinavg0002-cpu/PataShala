# PataShala

An Android adaptive-learning app for Classes 6–10. It works out each student's level, finds **which concept is weak and why**, picks the next step **and shows the reason**, and gives the teacher a class view where the teacher has the final say.

Team Alchemy · Code Kernel '26 · Round 2 (Build) · Adaptive Learning for Classes 6 to 10.


## What it does

1. **Student** registers (school, branch, class, section), picks a teacher for each subject; the **teacher approves**.
2. A short **diagnostic** starts at medium difficulty and moves up or down. Level = Basic / Medium / Strong.
3. Every answer is stored with difficulty, the *wrong-idea tag* of the option chosen, time taken and hints used.
4. The **engine** rebuilds each concept's status from the last 6 answers and names the most likely cause: English reading load, missing earlier skill, misconception, concept gap, or slip/guess.
5. The next step (lesson, worked example, simpler wording, go back to an earlier skill, harder question) comes with a **"Why this next step?"** panel.
6. The **teacher** sees the whole class: level mix, concept gaps, each student's strengths and weaknesses and the suggested cause, can **Confirm or Change** the cause, and can select students and **assign** a concept.

## Try it on a laptop (about 5 minutes, no phone needed)

You need **Python 3.11 or newer** and **Node.js (LTS)** installed. Open two terminals (PowerShell on Windows).

**Terminal 1: the server**

```
cd backend
python -m venv .venv
.venv\\Scripts\\python -m pip install -r requirements.txt
.venv\\Scripts\\python -m scripts.reset\_demo
.venv\\Scripts\\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

(On Mac or Linux use `.venv/bin/python` instead of `.venv\\Scripts\\python`.) Leave it running. `reset\_demo` loads the sample school data and takes a few seconds.

**Terminal 2: the app, in the browser**

```
cd mobile
npm install
npx expo start --web
```

Your browser opens the app (or open `http://localhost:8081`). On the first screen the server address is already `http://localhost:8000`; press **Connect**.

Tip: press F12 and switch to the phone-size view to see it as on a phone.

## Try it on an Android phone 

1. Install **Expo Go** from the Play Store (it must support SDK 58).
2. Put the phone and the laptop on the **same Wi-Fi**.
3. On the laptop, find its Wi-Fi address: open PowerShell and run `ipconfig`. Under **Wireless LAN adapter Wi-Fi**, copy the **IPv4 Address** (for example `192.168.1.23`).
4. Run Terminal 1 and `npx expo start` (without `--web`) in Terminal 2. Scan the QR code with Expo Go.
5. On the first screen type `http://192.168.1.23:8000` (your own address) and press **Connect**.

If the phone cannot connect, check that both are on the same Wi-Fi (not a guest network) and allow Python through the Windows firewall when asked.

## Sample accounts

All sample data is invented. Every PIN is `1234`.

|Role|Log in with|Notes|
|-|-|-|
|Student|`S10003`|Sunrise High School, Class 8-A. Has a mix of strong and weak concepts. Students are `S10001` to `S10018`.|
|Teacher|`T10001` or mobile `9000000001`|Maths 8-A and 8-B, Physical Science 8-A. `T10002` teaches Biology.|

To register a **new teacher**, choose Sunrise High School and enter the school teacher code `SH393511`. Any 10-digit mobile number that is not already used is accepted. New students pick a teacher, and the teacher approves them from the teacher home.

**Suggested path (5 minutes):**

1. Log in as `S10003`, open Mathematics, press Continue learning, answer a few questions, use a hint, then open **Show how the system decided**.
2. Open **How it works** and **See it in action**: the same question gives three different next steps for three students.
3. Log out, log in as `T10001`, open Mathematics 8-A, open a student, and press **Confirm** or **Change** on the suggested cause. Select two students and use **Group view** to assign a concept.

Tests: `cd backend` then `.venv\\Scripts\\python -m pytest -q` (36 tests). Type check: `cd mobile` then `npx tsc --noEmit`.

## What each checkpoint looks like in the app

|#|Checkpoint|How PataShala handles it|Where|
|-|-|-|-|
|1|Real adaptivity|Rule-based model of each concept (no chatbot, no ML). Status comes from the last 6 answers, weighted by difficulty and hints used.|`backend/app/engine.py`|
|2|Root gap|Prerequisite links between concepts, and five cause types with evidence: English reading load, missing earlier skill, misconception, concept gap, slip.|Student report, teacher student page|
|3|Few questions|Adaptive diagnostic that starts at medium and moves up or down. 10.2 questions on average in our simulation.|Simulation below|
|4|Poor internet|Runs on the school's local Wi-Fi with no internet needed, with small responses.|`backend/app`|
|5|Teaches, not tells|3 progressive hints per question, a lesson with a worked example, and a contrast example for a repeated wrong idea.|Practice screen|
|6|Fallback if AI is down|The system calls no AI service, so every answer comes from the rules and works with no outside service.|`backend/app/engine.py`|
|7|Proof it works|A simulation of 50 learners (below) and informal trials.|`backend/scripts/run\_simulation.py`|
|8|Safe data|PINs and login tokens are hashed, permissions are enforced on the server, a teacher sees only students who chose and were approved by that teacher, and only invented data is stored in this repository.|`backend/app/security.py`|
|9|Useful for teachers|Class concept-gap bars, level mix, filters, group view, assign, and Confirm/Change on the suggested cause.|Teacher screens|
|10|Curriculum fit|Telangana State Board, Class 8: Maths Ch 10, Physical Science Ch 1, Biological Science Ch 2. All questions and lessons are original.|`backend/app/catalog.py`|
|11|Language friendly|Plain English interface. Word problems have plain-wording versions, and the system detects when reading load is the cause.|Practice screen|
|12|Motivation|Hints instead of answers, no timers shown to the student, and a progress page with a donut and a next step.|Student Progress tab|
|13|Reliable data|An answer is accepted only for the student's current question, so a double tap is counted once (tested).|`test\_double\_tap\_on\_answer\_is\_counted\_once`|
|14|Build quality|Engine is pure functions with unit tests, the API is tested, and TypeScript type-checks.|`backend/tests`, `mobile/src`|

### Real-user testing

Getting real student responses and teacher data was hard in the time we had. We tried the app with relatives, siblings and neighbours, and they liked it. This is informal feedback, so we report no accuracy numbers from it.

and we are sorry that only class 8 with 3 subjects with each a single chapter is only functionable as this is a demo we will develop this project completely in near future.

### Simulation (not real students)

50 simulated learners with *invented* behaviour (seed 2026), compared with a fixed 10-question test:

|Measure|Adaptive engine|Fixed 10-question test|
|-|-|-|
|Weak-concept detection, precision / recall|0.81 / 1.00|1.00 / 0.74|
|English reading load found|14 of 14, 0 false flags|cannot detect|
|Strong students wrongly marked weak|2 of 8|—|
|Main cause matched the simulated truth|18 of 28|—|
|Average diagnostic questions|10.2|10|

This shows how the rules behave under our assumptions. It does **not** prove accuracy with real students. All thresholds are starting values that still need a pilot.

### Round 1 feedback → what we did

* *Name boards/languages, shared devices:* boards and states are listed in registration, and a shared-phone list (names and IDs only, never PINs) is on the login screen.
* *Worked example of different student paths:* the "Three students, one question" screen runs the real engine on three student types.
* *Measurable validation:* the simulation above, plus the teacher Confirm/Change count shown on the teacher home.

## Data and privacy

Everything in this repository is invented: names, schools, branches, mobile numbers, teacher codes and answers. No real student or teacher data and no secrets are included. The app runs on a local network, not the public internet.

