import React, { useEffect, useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { api, getCatalog } from '../api';
import { emptyProg, Prog, progressDone, ProgressForm, SchoolPicker } from '../forms';
import { useNav } from '../nav';
import { useAuth } from '../store';
import { C } from '../theme';
import { Btn, Card, Chip, ErrorBox, Field, H, Icon, Loading, Muted, Notice, Row, Screen, SegBar, T, Wrap } from '../ui';

const STEPS = ['School', 'Your details', 'Classes you teach', 'Your ID', 'Teaching progress'];

export default function TeacherReg() {
  const nav = useNav();
  const { signIn, user } = useAuth();
  const [step, setStep] = useState(0);
  const [cat, setCat] = useState<any>(null);
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  const [f, setF] = useState<any>({ school: null, branch: null, name: '', phone: '', pin: '', code: '' });
  const [rows, setRows] = useState<{ subject: string; class_no: number; section: string }[]>([]);
  const [draft, setDraft] = useState<any>({ subject: '', cls: null, section: '' });
  const [mine, setMine] = useState<any[]>([]);
  const [prog, setProg] = useState<Record<string, Prog>>({});
  const set = (p: any) => setF((o: any) => ({ ...o, ...p }));
  useEffect(() => { getCatalog().then(setCat).catch((e) => setErr(e.message)); }, []);
  if (!cat) return <Screen title="Teacher registration" onBack={() => nav.pop()}>{err ? <ErrorBox message={err} /> : <Loading />}</Screen>;

  const name = (id: string) => cat.subjects.find((s: any) => s.id === id)?.name ?? id;
  const canAdd = draft.subject && draft.cls && draft.section && !rows.some((r) => r.subject === draft.subject && r.class_no === draft.cls && r.section === draft.section);

  // Tell the teacher straight away if the school code is wrong, not at the very end.
  async function checkCode() {
    setBusy(true); setErr('');
    try { await api('/register/check-code', { body: { school_id: f.school, branch_id: f.branch, teacher_code: f.code, phone: f.phone } }); setStep(2); }
    catch (e: any) { setErr(e.message); } finally { setBusy(false); }
  }

  async function register() {
    setBusy(true); setErr('');
    try {
      const r = await api('/register/teacher', { body: { school_id: f.school, branch_id: f.branch, teacher_code: f.code, name: f.name, phone: f.phone, pin: f.pin, assignments: rows } });
      signIn(r);
      setMine(await api('/teacher/assignments'));
      setStep(3);
    } catch (e: any) { setErr(e.message); } finally { setBusy(false); }
  }
  async function saveProgress() {
    setBusy(true); setErr('');
    try {
      for (const a of mine) await api('/teacher/assignment-progress', { body: { assignment_id: a.id, ...(prog[String(a.id)] ?? emptyProg()) } });
      nav.reset('TeacherHome');
    } catch (e: any) { setErr(e.message); } finally { setBusy(false); }
  }

  let body: React.ReactNode; let footer: React.ReactNode;
  if (step === 0) {
    body = <SchoolPicker school={f.school} branch={f.branch} onChange={(s, b) => set({ school: s, branch: b })} />;
    footer = <Btn title="Next" onPress={() => setStep(1)} disabled={!(f.school && f.branch)} />;
  } else if (step === 1) {
    body = (
      <>
        <Field label="Full name" value={f.name} onChangeText={(t) => set({ name: t })} autoCap="words" />
        <Field label="Mobile number" value={f.phone} onChangeText={(t) => set({ phone: t.replace(/\D/g, '') })} keyboard="number-pad" maxLength={10} placeholder="10 digits. You can log in with it." />
        <Field label="School teacher code" value={f.code} onChangeText={(t) => set({ code: t.toUpperCase() })} autoCap="characters" placeholder="Given by your school office" />
        <Notice text="The school office issues this code. It proves you teach at this school, so only your own students can ever link to you." />
        <Field label="Choose a 4-digit PIN" value={f.pin} onChangeText={(t) => set({ pin: t.replace(/\D/g, '') })} secure keyboard="number-pad" maxLength={4} />
        {err ? <Notice text={err} icon="warning" tone="warn" /> : null}
      </>
    );
    footer = <Btn title="Next" onPress={checkCode} loading={busy} disabled={f.name.trim().length < 2 || !/^\d{10}$/.test(f.phone) || !f.code || f.pin.length !== 4} />;
  } else if (step === 2) {
    body = (
      <>
        <Notice text="Add every subject, class and section you teach. You can add as many as you need." />
        <H>Subject</H>
        <Wrap>{cat.subjects.map((s: any) => <Chip key={s.id} label={s.name} locked={!s.enabled} selected={draft.subject === s.id} onPress={() => setDraft({ ...draft, subject: s.id })} />)}</Wrap>
        <H>Class</H>
        <Wrap>{cat.classes.map((c: any) => <Chip key={c.no} label={`Class ${c.no}`} locked={!c.enabled} selected={draft.cls === c.no} onPress={() => setDraft({ ...draft, cls: c.no })} />)}</Wrap>
        <H>Section</H>
        <Wrap>{['A', 'B', 'C', 'D'].map((s) => <Chip key={s} label={`Section ${s}`} selected={draft.section === s} onPress={() => setDraft({ ...draft, section: s })} />)}</Wrap>
        <View style={{ height: 12 }} />
        <Btn title="Add this class" kind="soft" icon="add-circle" disabled={!canAdd} onPress={() => { setRows([...rows, { subject: draft.subject, class_no: draft.cls, section: draft.section }]); setDraft({ ...draft, section: '' }); }} />
        <H>Your classes ({rows.length})</H>
        {rows.length === 0 ? <Muted>None added yet.</Muted> : rows.map((r, i) => (
          <Card key={i} style={{ padding: 10, marginBottom: 6 }}>
            <Row><Icon name="school" color={C.teal} /><T bold style={{ flex: 1 }}>{name(r.subject)} · Class {r.class_no} · Section {r.section}</T>
              <Pressable onPress={() => setRows(rows.filter((_, j) => j !== i))} accessibilityLabel="Remove this class"><Icon name="trash" color={C.red} /></Pressable></Row>
          </Card>
        ))}
        {err ? <Notice text={err} icon="warning" tone="warn" /> : null}
      </>
    );
    footer = <Btn title="Create my ID" icon="id-card" onPress={register} loading={busy} disabled={rows.length === 0} />;
  } else if (step === 3) {
    body = (
      <>
        <View style={{ alignItems: 'center', marginVertical: 8 }}><Icon name="checkmark-circle" size={56} color={C.green} /><Text style={{ fontSize: 22, fontWeight: '800', color: C.ink, marginTop: 6 }}>You are registered</Text></View>
        <Card accent={C.teal} style={{ padding: 18 }}>
          <Muted>YOUR UNIQUE ID</Muted>
          <Text style={{ fontSize: 38, fontWeight: '800', color: C.teal, letterSpacing: 2 }}>{user?.code}</Text>
          <Text style={{ fontSize: 17, fontWeight: '700', color: C.ink, marginTop: 6 }}>{user?.name}</Text>
          <Muted>{user?.school} · {user?.branch}</Muted>
        </Card>
        <Notice text="Students at your school can now pick you for the classes you added." />
      </>
    );
    footer = <Btn title="Continue" onPress={() => setStep(4)} />;
  } else {
    body = (
      <>
        <Notice text="For each class, tell us what you are teaching now. Students see this when they pick their teacher." />
        <ProgressForm items={mine.map((a) => ({ key: String(a.id), subject: a.subject, title: `${a.subject_name} ${a.section}`, sub: `Class ${a.class_no}` }))} values={prog} onChange={setProg} />
        {err ? <Notice text={err} icon="warning" tone="warn" /> : null}
      </>
    );
    footer = <Btn title="Finish and open my classes" icon="home" onPress={saveProgress} loading={busy} disabled={!progressDone(mine.map((a) => String(a.id)), prog)} />;
  }
  return (
    <Screen title="Teacher registration" subtitle={`Step ${step + 1} of ${STEPS.length} · ${STEPS[step]}`} onBack={step === 3 ? undefined : () => (step > 0 && step < 3 ? setStep(step - 1) : nav.pop())} footer={footer}>
      <View style={{ marginBottom: 14 }}><SegBar height={6} parts={STEPS.map((_, i) => ({ value: 1, color: i <= step ? C.teal : C.line }))} /></View>
      {body}
    </Screen>
  );
}
