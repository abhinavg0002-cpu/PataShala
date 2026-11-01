import React, { useState } from 'react';
import { Text, View } from 'react-native';
import { api } from '../api';
import { useNav } from '../nav';
import { useAuth } from '../store';
import { C } from '../theme';
import { Btn, Card, Field, H, Icon, Muted, Notice, Row, Screen } from '../ui';

export default function Settings() {
  const nav = useNav();
  const { user, signOut } = useAuth();
  const [oldPin, setOld] = useState('');
  const [newPin, setNew] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const digits = (t: string) => t.replace(/\D/g, '');
  const change = async () => {
    setBusy(true); setMsg(null);
    try { await api('/me/change-pin', { body: { old_pin: oldPin, new_pin: newPin } }); setOld(''); setNew(''); setMsg({ ok: true, text: 'Your PIN was changed.' }); }
    catch (e: any) { setMsg({ ok: false, text: e.message }); }
    setBusy(false);
  };
  const line = (label: string, v?: string | number | null) => v ? <Row style={{ justifyContent: 'space-between', paddingVertical: 4 }}><Muted>{label}</Muted><Text style={{ color: C.ink, fontWeight: '600' }}>{v}</Text></Row> : null;
  return (
    <Screen title="Settings" subtitle={user?.role === 'teacher' ? 'Teacher account' : 'Student account'} tabs={user?.role === 'teacher' ? 'teacher' : 'student'}>
      <Card>
        <Row gap={12} style={{ marginBottom: 8 }}>
          <View style={{ width: 44, height: 44, borderRadius: 22, backgroundColor: C.tealBg, alignItems: 'center', justifyContent: 'center' }}><Icon name="person" color={C.teal} size={24} /></View>
          <Text style={{ fontSize: 18, fontWeight: '800', color: C.ink, flex: 1 }}>{user?.name}</Text>
        </Row>
        {line('ID', user?.code)}
        {line('Mobile', (user as any)?.phone)}
        {line('School', user?.school)}
        {line('Branch', user?.branch)}
        {user?.role === 'student' ? line('Class', `${user.class_no}-${user.section}`) : null}
        {user?.role === 'student' ? line('Roll number', user.roll_no) : null}
      </Card>
      <H>Change PIN</H>
      <Card>
        <Field label="Current PIN" value={oldPin} onChangeText={(t) => setOld(digits(t))} secure keyboard="number-pad" maxLength={4} />
        <Field label="New 4-digit PIN" value={newPin} onChangeText={(t) => setNew(digits(t))} secure keyboard="number-pad" maxLength={4} />
        {msg ? <Notice text={msg.text} icon={msg.ok ? 'checkmark-circle' : 'warning'} tone={msg.ok ? 'info' : 'warn'} /> : null}
        <Btn title="Change PIN" icon="key" onPress={change} loading={busy} disabled={oldPin.length !== 4 || newPin.length !== 4} />
      </Card>
      <H>Account</H>
      <Btn title="Log out" kind="ghost" icon="log-out-outline" onPress={() => { signOut(); nav.reset('Welcome'); }} />
    </Screen>
  );
}
