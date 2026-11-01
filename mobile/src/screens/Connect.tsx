import React, { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { api, getBase, setBase, store } from '../api';
import { APP_NAME, TEAM } from '../config';
import { useNav } from '../nav';
import { C } from '../theme';
import { Btn, Field, Icon, Muted, Notice } from '../ui';

export default function Connect() {
  const nav = useNav();
  const ins = useSafeAreaInsets();
  const [url, setUrl] = useState(getBase());
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');

  useEffect(() => { store('server_url').then((u) => { if (u) { setBase(u); setUrl(u); } }); }, []);

  async function go() {
    setBusy(true); setErr('');
    setBase(url);
    try {
      await api('/health');
      await store('server_url', getBase());
      nav.replace('Welcome');
    } catch (e: any) {
      setErr(e.message);
    } finally { setBusy(false); }
  }

  return (
    <View style={{ flex: 1, backgroundColor: C.primary, paddingTop: ins.top + 40, paddingHorizontal: 22 }}>
      <View style={{ alignItems: 'center', marginBottom: 28 }}>
        <View style={{ width: 84, height: 84, borderRadius: 28, backgroundColor: C.teal, alignItems: 'center', justifyContent: 'center', marginBottom: 16 }}>
          <Icon name="school" size={44} color="#fff" />
        </View>
        <Text style={{ color: '#fff', fontSize: 28, fontWeight: '800' }}>{APP_NAME}</Text>
        <Text style={{ color: '#D5DEE9', fontSize: 15, marginTop: 4, textAlign: 'center' }}>Adaptive learning for Classes 6–10</Text>
        <Text style={{ color: '#9FB0C5', fontSize: 12, marginTop: 4 }}>{TEAM}</Text>
      </View>
      <View style={{ backgroundColor: '#fff', borderRadius: 22, padding: 18 }}>
        <Text style={{ fontSize: 17, fontWeight: '800', color: C.ink, marginBottom: 4 }}>Connect to the school server</Text>
        <Muted style={{ marginBottom: 12 }}>Enter the school server's Wi-Fi address. Your phone must be on the same Wi-Fi.</Muted>
        <Field label="Server address" value={url} onChangeText={setUrl} keyboard="url" placeholder="http://192.168.1.10:8000" />
        {err ? <Notice text={err} icon="warning" tone="warn" /> : null}
        <Btn title="Connect" icon="wifi" onPress={go} loading={busy} />
      </View>
    </View>
  );
}
