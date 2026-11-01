import React, { useState } from 'react';
import { api } from '../api';
import { useNav } from '../nav';
import { Btn, Chip, Field, H, Muted, Notice, Row, Screen } from '../ui';

export default function ForgotPin() {
  const nav = useNav();
  const [role, setRole] = useState<'teacher' | 'student'>('teacher');
  const [f, setF] = useState({ who: '', code: '', roll: '', section: '', pin: '' });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');
  const [done, setDone] = useState(false);
  const set = (p: any) => setF((o) => ({ ...o, ...p }));
  const ready = f.who.length >= 3 && f.pin.length === 4 && (role === 'teacher' ? f.code : f.roll && f.section);
  const go = async () => {
    setBusy(true); setErr('');
    try {
      await api('/auth/reset-pin', { body: { who: f.who.trim(), new_pin: f.pin, teacher_code: role === 'teacher' ? f.code : '', roll_no: role === 'student' ? f.roll : '', section: role === 'student' ? f.section : '' } });
      setDone(true);
    } catch (e: any) { setErr(e.message); }
    setBusy(false);
  };
  if (done) return (
    <Screen title="PIN changed" footer={<Btn title="Go to log in" icon="log-in" onPress={() => nav.reset('Login')} />}>
      <Notice icon="checkmark-circle" text="Your new PIN is ready. Log in with it now." />
    </Screen>
  );
  return (
    <Screen title="Forgot PIN" subtitle="Set a new PIN" footer={<Btn title="Set new PIN" icon="key" onPress={go} loading={busy} disabled={!ready} />}>
      <Row style={{ marginBottom: 12 }}>
        <Chip label="I am a teacher" selected={role === 'teacher'} onPress={() => setRole('teacher')} />
        <Chip label="I am a student" selected={role === 'student'} onPress={() => setRole('student')} />
      </Row>
      {role === 'teacher' ? (
        <>
          <Field label="Your mobile number or ID" value={f.who} onChangeText={(t) => set({ who: t.toUpperCase() })} autoCap="characters" />
          <Field label="School teacher code" value={f.code} onChangeText={(t) => set({ code: t.toUpperCase() })} autoCap="characters" placeholder="Given by your school office" />
        </>
      ) : (
        <>
          <Field label="Your ID (for example S10001)" value={f.who} onChangeText={(t) => set({ who: t.toUpperCase() })} autoCap="characters" />
          <Field label="Roll number" value={f.roll} onChangeText={(t) => set({ roll: t.replace(/\D/g, '') })} keyboard="number-pad" maxLength={4} />
          <Field label="Section (A, B, C or D)" value={f.section} onChangeText={(t) => set({ section: t.toUpperCase().slice(0, 1) })} autoCap="characters" maxLength={1} />
        </>
      )}
      <H>New PIN</H>
      <Field label="New 4-digit PIN" value={f.pin} onChangeText={(t) => set({ pin: t.replace(/\D/g, '') })} secure keyboard="number-pad" maxLength={4} />
      {err ? <Notice text={err} icon="warning" tone="warn" /> : null}
      <Muted>We check these details against your registration before the PIN changes.</Muted>
    </Screen>
  );
}
