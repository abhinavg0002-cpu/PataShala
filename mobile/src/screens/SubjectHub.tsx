import React, { useState } from 'react';
import { Text, View } from 'react-native';
import { api, getCatalog } from '../api';
import { useNav } from '../nav';
import { C } from '../theme';
import { Btn, Card, Choice, ErrorBox, H, Icon, LevelBadge, Loading, Muted, Notice, Row, Screen, Tag, useLoad } from '../ui';

export default function SubjectHub({ params }: { params: any }) {
  const nav = useNav();
  const { subject, name } = params;
  const subs = useLoad<any[]>(() => api('/student/subjects'), [subject]);
  const opts = useLoad<any[]>(() => api('/student/options', { params: { subject } }), [subject]);
  const cat = useLoad<any>(() => getCatalog());
  const chapter = cat.data ? cat.data.chapters[subject]?.find((c: any) => c.title === cat.data.demo_chapter[subject]) : null;
  const [pick, setPick] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');
  const s = subs.data?.find((x) => x.id === subject);
  const enroll = async () => {
    if (pick == null) return;
    setBusy(true); setErr('');
    try { await api('/student/enroll', { body: { subject, assignment_id: pick } }); subs.reload(); } catch (e: any) { setErr(e.message); }
    setBusy(false);
  };
  const en = s?.enrollment;
  return (
    <Screen title={name} subtitle="Telangana State Board · Class 8" tabs="student">
      {subs.loading ? <Loading /> : subs.error ? <ErrorBox message={subs.error} onRetry={subs.reload} /> : (
        <>
          {chapter ? (
            <Card accent={C.teal}>
              <Row gap={12}>
                <Icon name="book" color={C.teal} size={26} />
                <View style={{ flex: 1 }}><Muted>Chapter</Muted><Text style={{ fontWeight: '800', color: C.ink, fontSize: 16 }}>{chapter.no ? `Ch ${chapter.no} · ` : ''}{chapter.title}</Text></View>
              </Row>
            </Card>
          ) : null}
          <H>Your teacher</H>
          {en ? (
            <Card accent={en.status === 'approved' ? C.green : C.amber}>
              <Row><Icon name={en.status === 'approved' ? 'checkmark-circle' : 'time'} color={en.status === 'approved' ? C.green : C.amber} size={22} />
                <Text style={{ flex: 1, fontWeight: '700', color: C.ink }}>{en.teacher}</Text><Tag text={en.status === 'approved' ? 'Approved' : 'Waiting for approval'} /></Row>
              {en.status !== 'approved' ? <Muted style={{ marginTop: 6 }}>You can still start the test. Your teacher sees your results once they approve.</Muted> : null}
            </Card>
          ) : (
            <>
              <Muted style={{ marginBottom: 8 }}>Teachers who teach {name} to your class and section:</Muted>
              {opts.loading ? <Loading /> : opts.data?.length ? opts.data.map((o) => (
                <Choice key={o.assignment_id} title={o.teacher} icon="person" sub={`Class ${o.class_no}-${o.section}${o.teaching?.current_chapter ? ` · now teaching: ${o.teaching.current_chapter}` : ''}`} selected={pick === o.assignment_id} onPress={() => setPick(o.assignment_id)} />
              )) : <Notice tone="warn" text="No teacher has added this subject for your class and section yet." />}
              {err ? <ErrorBox message={err} /> : null}
              <Btn title="Request this teacher" icon="send" disabled={pick == null} loading={busy} onPress={enroll} />
            </>
          )}
          <H>Your level</H>
          <Card>
            <Row><LevelBadge level={s.level} big /><Muted style={{ flex: 1 }}>{s.level ? `${s.answered} questions answered so far.` : 'Take the short diagnostic to find your level.'}</Muted></Row>
          </Card>
          <Btn title={s.answered === 0 ? 'Start diagnostic' : 'Continue learning'} icon="play" onPress={() => nav.push('Practice', { subject, name })} style={{ marginBottom: 10 }} />
          <Btn title="My report" kind="ghost" icon="stats-chart" disabled={s.answered === 0} onPress={() => nav.push('Report', { subject, name })} />
        </>
      )}
    </Screen>
  );
}
