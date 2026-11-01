import React from 'react';
import { Text, View } from 'react-native';
import { useAuth } from '../store';
import { useNav } from '../nav';
import { C, SUBJECT_ICON } from '../theme';
import { Bar, Btn, Card, ErrorBox, H, Icon, LevelBadge, Loading, Muted, Row, Screen, Tag, useLoad } from '../ui';
import { api } from '../api';

const mastery = (c: any) => { const n = c.secure + c.developing + c.needs_support; return n ? (c.secure + 0.5 * c.developing) / n : 0; };

export default function StudentHome() {
  const nav = useNav();
  const { user } = useAuth();
  const { data, error, loading, reload } = useLoad<any[]>(() => api('/student/subjects'));
  const subjects = (data ?? []).filter((s) => s.enabled);
  const next = subjects.find((s) => s.answered > 0 && s.level !== 'Strong') ?? subjects[0];
  return (
    <Screen title={`Hello, ${user?.name.split(' ')[0]}`} subtitle={`Class ${user?.class_no}-${user?.section} · ${user?.school}`} tall tabs="student">
      {loading ? <Loading /> : error ? <ErrorBox message={error} onRetry={reload} /> : (
        <>
          {next ? (
            <Card style={{ backgroundColor: C.primary, borderColor: C.primary, marginTop: -4 }}>
              <Muted style={{ color: '#9FB0C5' }}>{next.answered ? 'Continue where you left off' : 'Start here'}</Muted>
              <Text style={{ color: '#fff', fontSize: 20, fontWeight: '800', marginTop: 2 }}>{next.name}</Text>
              <Row style={{ marginVertical: 8 }}>
                {next.level ? <Tag text={`${next.level} level`} color={C.primary} bg="#fff" icon="speedometer" /> : <Tag text="Level not found yet" color={C.primary} bg="#fff" />}
                <Tag text={`${next.answered} answered`} color="#fff" bg="rgba(255,255,255,0.15)" />
              </Row>
              <Btn title={next.answered ? 'Continue learning' : 'Start diagnostic'} icon="play" onPress={() => nav.push('Practice', { subject: next.id, name: next.name })} />
            </Card>
          ) : null}
          <H>Your subjects</H>
          {(data ?? []).map((s) => !s.enabled ? (
            <Card key={s.id}>
              <Row gap={12}>
                <View style={{ width: 44, height: 44, borderRadius: 12, backgroundColor: C.tealBg, alignItems: 'center', justifyContent: 'center' }}><Icon name={SUBJECT_ICON[s.id] ?? 'book'} color={C.teal} size={24} /></View>
                <View style={{ flex: 1 }}><Text style={{ fontSize: 16, fontWeight: '800', color: C.ink }}>{s.name}</Text></View>
              </Row>
            </Card>
          ) : (
            <Card key={s.id} onPress={() => nav.push('SubjectHub', { subject: s.id, name: s.name })}>
              <Row gap={12}>
                <View style={{ width: 44, height: 44, borderRadius: 12, backgroundColor: C.tealBg, alignItems: 'center', justifyContent: 'center' }}><Icon name={SUBJECT_ICON[s.id] ?? 'book'} color={C.teal} size={24} /></View>
                <View style={{ flex: 1 }}>
                  <Text style={{ fontSize: 16, fontWeight: '800', color: C.ink }}>{s.name}</Text>
                  <Muted>{s.enrollment ? `${s.enrollment.teacher}${s.enrollment.status === 'approved' ? '' : ' · awaiting approval'}` : 'Choose your teacher'}</Muted>
                </View>
                <LevelBadge level={s.level} />
              </Row>
              {s.answered > 0 ? (
                <View style={{ marginTop: 12 }}>
                  <Bar value={mastery(s.counts)} label="Chapter mastery" right={`${s.counts.secure} of ${s.counts.secure + s.counts.developing + s.counts.needs_support} secure`} />
                </View>
              ) : <Muted style={{ marginTop: 8 }}>Take the short diagnostic to find your level.</Muted>}
            </Card>
          ))}
        </>
      )}
    </Screen>
  );
}
