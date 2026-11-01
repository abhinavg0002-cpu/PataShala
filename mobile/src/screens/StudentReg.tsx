import React, { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import { api, getCatalog } from '../api';
import { emptyProg, Prog, progressDone, ProgressForm, SchoolPicker } from '../forms';
import { useNav } from '../nav';
import { useAuth } from '../store';
import { C } from '../theme';
import { Btn, Card, Chip, Choice, ErrorBox, Field, H, Icon, Loading, Muted, Notice, Row, Screen, SegBar, T, Wrap } from '../ui';

const STEPS = ['School', 'About you', 'Board & place', 'Teachers', 'Your ID', 'Academic year'];

export default function StudentReg() {
  const nav = useNav();
  const { signIn, user } = useAuth();
  const [step, setStep] = useState(0);
  const [cat, setCat] = useState<any>(null);
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  const [f, setF] = useState<any>({ school: null, branch: null, name: '', roll: '', cls: null, section: '', gender: '', board: '', state: '', area: '', locality: '', pin: '' });
  const [options, setOptions] = useState<Record<string, any[]>>({});
  const [picked, setPicked] = useState<Record<string, number>>({});
  const [prog, setProg] = useState<Record<string, Prog>>({});
  const set = (p: any) => setF((o: any) => ({ ...o, ...p }));

  useEffect(() => { getCatalog().then(setCat).catch((e) => setErr(e.message)); }, []);

  const back = () => (step > 0 && step < 4 ? setStep(step - 1) : nav.pop());
  const demoSubjects = cat?.subjects.filter((s: any) => s.enabled) ?? [];

  async function createAccount() {
    setBusy(true); setErr('');
    try {
      const r = await api('/register/student', { body: { school_id: f.school, branch_id: f.branch, name: f.name, roll_no: f.roll, class_no: f.cls, section: f.section, gender: f.gender, board: f.board, state: f.state, locality: f.locality, pin: f.pin } });
      signIn(r);
      const opts: Record<string, any[]> = {};
      for (const s of demoSubjects) opts[s.id] = await api('/student/options', { params: { subject: s.id } });
      setOptions(opts);
      setStep(3);
    } catch (e: any) { setErr(e.message); } finally { setBusy(false); }
  }

  async function saveTeachers() {
    setBusy(true); setErr('');
    try {
      for (const s of demoSubjects) if (picked[s.id]) await api('/student/enroll', { body: { subject: s.id, assignment_id: picked[s.id] } });
      setStep(4);
    } catch (e: any) { setErr(e.message); } finally { setBusy(false); }
  }

  async function saveProgress() {
    setBusy(true); setErr('');
    try {
      for (const s of demoSubjects) {
        const p = prog[s.id] ?? emptyProg();
        await api('/student/progress', { body: { subject: s.id, ...p } });
      }
      nav.reset('StudentHome');
    } catch (e: any) { setErr(e.message); } finally { setBusy(false); }
  }

  if (!cat) return <Screen title="Student registration" onBack={() => nav.pop()}>{err ? <ErrorBox message={err} /> : <Loading />}</Screen>;

  const valid0 = f.school && f.branch;
  const valid1 = f.name.trim().length >= 2 && /^\d{1,4}$/.test(f.roll) && f.cls && f.section && f.gender;
  const valid2 = f.board && f.state && f.pin.length === 4;
  const allTeachers = demoSubjects.every((s: any) => !options[s.id]?.length || picked[s.id]);

  let body: React.ReactNode = null;
  let footer: React.ReactNode = null;
  if (step === 0) {
    body = <SchoolPicker school={f.school} branch={f.branch} onChange={(s, b) => set({ school: s, branch: b })} />;
    footer = <Btn title="Next" onPress={() => setStep(1)} disabled={!valid0} />;
  } else if (step === 1) {
    body = (
      <>
        <Field label="Full name" value={f.name} onChangeText={(t) => set({ name: t })} autoCap="words" placeholder="Student name" />
        <Field label="Roll number" value={f.roll} onChangeText={(t) => set({ roll: t.replace(/\D/g, '') })} keyboard="number-pad" maxLength={4} />
        <H>Class</H>
        <Wrap>{cat.classes.map((c: any) => <Chip key={c.no} label={`Class ${c.no}`} selected={f.cls === c.no} locked={!c.enabled} onPress={() => set({ cls: c.no })} />)}</Wrap>
        <H>Section</H>
        <Wrap>{['A', 'B', 'C', 'D'].map((s) => <Chip key={s} label={`Section ${s}`} selected={f.section === s} onPress={() => set({ section: s })} />)}</Wrap>
        <H>Gender</H>
        <Wrap>{['Girl', 'Boy'].map((g) => <Chip key={g} label={g} selected={f.gender === g} onPress={() => set({ gender: g })} />)}</Wrap>
      </>
    );
    footer = <Btn title="Next" onPress={() => setStep(2)} disabled={!valid1} />;
  } else if (step === 2) {
    body = (
      <>
        <H>Board</H>
        {cat.boards.map((b: any) => <Choice key={b.id} title={b.name} icon="ribbon" locked={!b.enabled} selected={f.board === b.id} onPress={() => set({ board: b.id })} />)}
        <H>State</H>
        <Wrap>{cat.states.map((s: any) => <Chip key={s.id} label={s.name} locked={!s.enabled} selected={f.state === s.id} onPress={() => set({ state: s.id })} />)}</Wrap>
        <Field label="Locality / mandal (optional)" value={f.locality} onChangeText={(t) => set({ locality: t })} autoCap="words" />
        <H>Choose a 4-digit PIN</H>
        <Muted style={{ marginBottom: 8 }}>You will use your ID and this PIN to log in. Do not share it.</Muted>
        <Field label="PIN" value={f.pin} onChangeText={(t) => set({ pin: t.replace(/\D/g, '') })} secure keyboard="number-pad" maxLength={4} />
        {err ? <Notice text={err} icon="warning" tone="warn" /> : null}
      </>
    );
    footer = <Btn title="Create my ID" icon="id-card" onPress={createAccount} loading={busy} disabled={!valid2} />;
  } else if (step === 3) {
    body = (
      <>
        <Notice text="Pick who teaches each subject to your class and section. Your teacher approves the link, then sees your progress." />
        
        {cat.subjects.map((s: any) => {
          if (!s.enabled) return <Choice key={s.id} title={s.name} locked icon="book" />;
          const list = options[s.id] ?? [];
          return (
            <Card key={s.id}>
              <Row><Icon name="book" color={C.primary} /><T bold style={{ flex: 1 }}>{s.name}</T></Row>
              {list.length === 0 ? <Muted style={{ marginTop: 6 }}>No teacher has registered for this subject in Class {f.cls}, Section {f.section} at this branch yet.</Muted> : (
                <View style={{ marginTop: 8 }}>
                  {list.map((o) => (
                    <Choice key={o.assignment_id} title={o.teacher} icon="person" selected={picked[s.id] === o.assignment_id}
                      sub={o.teaching?.current_chapter ? `Teaching now: ${o.teaching.current_chapter}` : `Class ${o.class_no} · Section ${o.section}`}
                      onPress={() => setPicked({ ...picked, [s.id]: o.assignment_id })} />
                  ))}
                </View>
              )}
            </Card>
          );
        })}
        {err ? <Notice text={err} icon="warning" tone="warn" /> : null}
      </>
    );
    footer = <Btn title="Next" onPress={saveTeachers} loading={busy} disabled={!allTeachers} />;
  } else if (step === 4) {
    body = (
      <>
        <View style={{ alignItems: 'center', marginVertical: 8 }}>
          <Icon name="checkmark-circle" size={56} color={C.green} />
          <Text style={{ fontSize: 22, fontWeight: '800', color: C.ink, marginTop: 6 }}>You are registered</Text>
        </View>
        <Card accent={C.primary} style={{ padding: 18 }}>
          <Muted>YOUR UNIQUE ID</Muted>
          <Text style={{ fontSize: 38, fontWeight: '800', color: C.primary, letterSpacing: 2 }} accessibilityLabel={`Your ID is ${user?.code}`}>{user?.code}</Text>
          <Text style={{ fontSize: 17, fontWeight: '700', color: C.ink, marginTop: 6 }}>{user?.name}</Text>
          <Muted>Class {user?.class_no} · Section {user?.section} · Roll {user?.roll_no}</Muted>
          <Muted>{user?.school} · {user?.branch}</Muted>
          <Muted>{user?.area_type} · Telangana State Board</Muted>
        </Card>
        <Notice text="Remember your ID and PIN. You need both to log in again." />
      </>
    );
    footer = <Btn title="Continue" onPress={() => setStep(5)} />;
  } else {
    body = (
      <>
        <Notice text="Tell us where your class is in each subject, so the test starts in the right place." />
        <ProgressForm items={cat.subjects.map((s: any) => ({ key: s.id, subject: s.id, title: s.name, enabled: s.enabled }))} values={prog} onChange={setProg} />
        {err ? <Notice text={err} icon="warning" tone="warn" /> : null}
      </>
    );
    footer = <Btn title="Finish and go to my home" icon="home" onPress={saveProgress} loading={busy} disabled={!progressDone(demoSubjects.map((x: any) => x.id), prog)} />;
  }

  return (
    <Screen title="Student registration" subtitle={`Step ${step + 1} of ${STEPS.length} · ${STEPS[step]}`} onBack={step === 4 ? undefined : back} footer={footer}>
      <View style={{ marginBottom: 14 }}><SegBar height={6} parts={STEPS.map((_, i) => ({ value: 1, color: i <= step ? C.primary : C.line }))} /></View>
      {body}
    </Screen>
  );
}
