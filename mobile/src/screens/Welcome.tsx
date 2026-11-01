import React from 'react';
import { ScrollView, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { APP_NAME } from '../config';
import { useNav } from '../nav';
import { C, R } from '../theme';
import { Btn, Card, H, Icon, Muted, Row } from '../ui';

function Big({ icon, title, sub, onPress, color }: { icon: string; title: string; sub: string; onPress: () => void; color: string }) {
  return (
    <Card onPress={onPress} style={{ padding: 18 }}>
      <Row gap={14}>
        <View style={{ width: 54, height: 54, borderRadius: 18, backgroundColor: color, alignItems: 'center', justifyContent: 'center' }}><Icon name={icon} size={28} color="#fff" /></View>
        <View style={{ flex: 1 }}>
          <Text style={{ fontSize: 18, fontWeight: '800', color: C.ink }}>{title}</Text>
          <Muted>{sub}</Muted>
        </View>
        <Icon name="chevron-forward" color={C.mute} />
      </Row>
    </Card>
  );
}

export default function Welcome() {
  const nav = useNav();
  const ins = useSafeAreaInsets();
  return (
    <View style={{ flex: 1, backgroundColor: C.bg }}>
      <View style={{ backgroundColor: C.primary, paddingTop: ins.top + 24, paddingBottom: 30, paddingHorizontal: 20, borderBottomLeftRadius: 22, borderBottomRightRadius: 22 }}>
        <Text style={{ color: '#9FB0C5', fontSize: 12, fontWeight: '700', letterSpacing: 1 }}>WELCOME TO</Text>
        <Text style={{ color: '#fff', fontSize: 26, fontWeight: '800' }}>{APP_NAME}</Text>
        <Text style={{ color: '#D5DEE9', fontSize: 15, marginTop: 6 }}>Finds what each student finds hard, and why. Then picks the next step, with the reason shown.</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <H>Who are you?</H>
        <Big icon="person" title="I am a student" sub="Register, take a short test, get your plan" color={C.primary} onPress={() => nav.push('StudentReg')} />
        <Big icon="people" title="I am a teacher" sub="Join with your school's teacher code" color={C.teal} onPress={() => nav.push('TeacherReg')} />
        <Btn title="I already have an ID · Log in" kind="ghost" icon="log-in" onPress={() => nav.push('Login')} style={{ marginBottom: 14 }} />

        <H>See how it works</H>
        <Card onPress={() => nav.push('Explainer')} accent={C.primary}>
          <Row><Icon name="git-network" color={C.primary} size={22} /><View style={{ flex: 1 }}><Text style={{ fontWeight: '800', color: C.ink }}>How the system decides</Text><Muted>Levels, causes and next steps in one picture</Muted></View><Icon name="chevron-forward" color={C.mute} /></Row>
        </Card>
        <Card onPress={() => nav.push('Replay')} accent={C.teal}>
          <Row><Icon name="people-circle" color={C.teal} size={22} /><View style={{ flex: 1 }}><Text style={{ fontWeight: '800', color: C.ink }}>Three students, one question</Text><Muted>Same question, three different next steps</Muted></View><Icon name="chevron-forward" color={C.mute} /></Row>
        </Card>

        <View style={{ height: 24 }} />
      </ScrollView>
    </View>
  );
}
