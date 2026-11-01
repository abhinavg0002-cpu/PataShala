import React, { useState } from 'react';
import { Text, View } from 'react-native';
import { api } from '../api';
import { useAuth } from '../store';
import { useNav } from '../nav';
import { C, SUBJECT_ICON } from '../theme';
import { Bar, Btn, Card, Donut, ErrorBox, H, Icon, Loading, Muted, Notice, Row, Screen, Tag, useLoad } from '../ui';

export default function TeacherHome() {
  const nav = useNav();
  const { user } = useAuth();
  const cls = useLoad<any[]>(() => api('/teacher/assignments'));
  const req = useLoad<any[]>(() => api('/teacher/requests'));
  const st = useLoad<any>(() => api('/teacher/stats'));
  const [err, setErr] = useState('');
  const review = async (id: number, approve: boolean) => {
    try { await api(`/teacher/requests/${id}`, { body: { approve } }); req.reload(); cls.reload(); } catch (e: any) { setErr(e.message); }
  };
  return (
    <Screen title={user?.name ?? 'Teacher'} subtitle={`${user?.school} · ${user?.branch}`} tall tabs="teacher">
      {err ? <ErrorBox message={err} /> : null}
      <H>Join requests{req.data?.length ? ` (${req.data.length})` : ''}</H>
      {req.loading ? <Loading /> : req.error ? <ErrorBox message={req.error} onRetry={req.reload} /> : req.data!.length === 0 ? <Muted style={{ marginBottom: 12 }}>No pending requests.</Muted> : req.data!.map((r) => (
        <Card key={r.id} accent={C.amber}>
          <Text style={{ fontWeight: '800', color: C.ink }}>{r.student} · roll {r.roll_no}</Text>
          <Muted>{r.subject} · Class {r.class_no}-{r.section} · {r.code}</Muted>
          <Row style={{ marginTop: 8 }}>
            <Btn title="Approve" icon="checkmark" onPress={() => review(r.id, true)} style={{ flex: 1, minHeight: 42 }} />
            <Btn title="Reject" kind="ghost" onPress={() => review(r.id, false)} style={{ flex: 1, minHeight: 42 }} />
          </Row>
        </Card>
      ))}
      <H>My classes</H>
      {cls.loading ? <Loading /> : cls.error ? <ErrorBox message={cls.error} onRetry={cls.reload} /> : cls.data!.map((a) => (
        <Card key={a.id} accent={C.teal} onPress={() => nav.push('Roster', { id: a.id, title: `${a.subject_name} · ${a.class_no}-${a.section}` })}>
          <Row gap={12}>
            <Icon name={SUBJECT_ICON[a.subject] ?? 'book'} color={C.teal} size={26} />
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 16, fontWeight: '800', color: C.ink }}>{a.subject_name} · Class {a.class_no}-{a.section}</Text>
              <Muted>{a.students} students{a.pending ? ` · ${a.pending} waiting` : ''}{a.progress?.current_chapter ? ` · teaching: ${a.progress.current_chapter}` : ''}</Muted>
            </View>
            <Icon name="chevron-forward" color={C.mute} />
          </Row>
          {a.students > 0 ? (
            <Row gap={14} style={{ marginTop: 12 }}>
              <Donut size={84} stroke={11} center={String(a.students)} caption="students"
                segments={[{ value: a.levels.Strong, color: C.green }, { value: a.levels.Medium, color: C.blue }, { value: a.levels.Basic, color: C.orange }, { value: a.levels['Not tested'], color: C.mute }]} />
              <View style={{ flex: 1 }}>
                <Muted>Strong {a.levels.Strong} · Medium {a.levels.Medium} · Basic {a.levels.Basic} · Not tested {a.levels['Not tested']}</Muted>
                {a.weakest.slice(0, 2).map((w: any) => <Bar key={w.concept} value={w.students / a.students} color={C.orange} label={w.concept} right={`${w.students} need support`} height={8} />)}
              </View>
            </Row>
          ) : null}
        </Card>
      ))}
      <H>How often you agree with the system</H>
      {st.data ? (
        <Card>
          {st.data.decisions === 0 ? <Muted>No decisions yet. Open a student and confirm or change the suggested cause.</Muted> : (
            <Row><Tag text={`${st.data.decisions} decisions`} /><Tag text={`${st.data.confirmed} confirmed`} color={C.green} bg={C.greenBg} /><Tag text={`${st.data.overridden} changed`} color={C.orange} bg={C.orangeBg} /></Row>
          )}
        </Card>
      ) : null}
      <Notice icon="shield-checkmark" text="You only see students who chose you for that subject and whom you approved. This is checked on the server." />
    </Screen>
  );
}
