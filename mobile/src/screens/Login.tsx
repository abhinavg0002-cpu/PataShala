import React, { useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { api } from '../api';
import { useNav } from '../nav';
import { useAuth } from '../store';
import { C } from '../theme';
import { Btn, Card, Field, H, Icon, Muted, Notice, Row, Screen } from '../ui';

export default function Login({ params }: { params?: { code?: string } }) {
  const nav = useNav();
  const { known, signIn, forget } = useAuth();
  const [code, setCode] = useState(params?.code ?? '');
  const [pin, setPin] = useState('');
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);

  async function go() {
    setBusy(true); setErr('');
    try {
      const r = await api('/auth/login', { body: { code, pin } });
      signIn(r);
      nav.reset(r.user.role === 'teacher' ? 'TeacherHome' : 'StudentHome');
    } catch (e: any) { setErr(e.message); setPin(''); } finally { setBusy(false); }
  }

  return (
    <Screen title="Log in" subtitle="Use your ID and 4-digit PIN" onBack={() => nav.pop()}>
      {known.length > 0 ? (
        <>
          <H>Who is using this phone?</H>
          <Muted style={{ marginBottom: 8 }}>Sharing this phone? Tap your name, then type your PIN. PINs are never saved on the phone.</Muted>
          {known.map((k) => (
            <Card key={k.code} onPress={() => { setCode(k.code); setPin(''); setErr(''); }} accent={code === k.code ? C.primary : undefined} style={{ marginBottom: 8 }}>
              <Row>
                <View style={{ width: 36, height: 36, borderRadius: 18, backgroundColor: C.violetBg, alignItems: 'center', justifyContent: 'center' }}><Text style={{ fontWeight: '800', color: C.primary }}>{k.name[0]}</Text></View>
                <View style={{ flex: 1 }}><Text style={{ fontWeight: '700', color: C.ink }}>{k.name}</Text><Muted>{k.role} · {k.code}</Muted></View>
                <Pressable onPress={() => forget(k.code)} accessibilityLabel={`Remove ${k.name} from this phone`}><Icon name="close-circle" color={C.mute} /></Pressable>
              </Row>
            </Card>
          ))}
        </>
      ) : null}
      <H>Your ID and PIN</H>
      <Field label="ID, or mobile number for teachers" value={code} onChangeText={(t) => setCode(t.toUpperCase())} autoCap="characters" />
      <Field label="PIN (4 digits)" value={pin} onChangeText={(t) => setPin(t.replace(/\D/g, ''))} secure keyboard="number-pad" maxLength={4} />
      {err ? <Notice text={err} icon="warning" tone="warn" /> : null}
      <Btn title="Log in" icon="log-in" onPress={go} loading={busy} disabled={code.length < 3 || pin.length !== 4} />
      <Btn title="Forgot PIN?" kind="soft" onPress={() => nav.push('ForgotPin')} style={{ marginTop: 10 }} />
    </Screen>
  );
}
