import React, { useState } from 'react';
import { Text, View } from 'react-native';
import { api } from '../api';
import { useNav } from '../nav';
import { C, CAUSE, STATUS } from '../theme';
import { clean } from '../trace';
import { Bar, Btn, Card, Chip, CausePill, ErrorBox, H, LevelBadge, LevelMeter, Loading, Muted, Notice, Row, Screen, StatusPill, Tag, Wrap, useLoad } from '../ui';

function Review({ c, sid, subject, done }: { c: any; sid: number; subject: string; done: () => void }) {
  const top = c.causes[0];
  const [other, setOther] = useState(false);
  const [err, setErr] = useState('');
  const send = async (action: string, final: string) => {
    try { await api('/teacher/decision', { body: { student_id: sid, subject, concept_id: c.id, system_cause: top.type, action, final_cause: final } }); done(); } catch (e: any) { setErr(e.message); }
  };
  if (c.decision) return <Tag text={`You ${c.decision.action === 'confirm' ? 'confirmed' : 'changed it to ' + CAUSE[c.decision.final_cause]?.label}`} color={C.green} bg={C.greenBg} icon="checkmark-circle" />;
  return (
    <View style={{ marginTop: 8 }}>
      {err ? <Muted style={{ color: C.red }}>{err}</Muted> : null}
      <Row>
        <Btn title="Confirm" icon="checkmark" onPress={() => send('confirm', top.type)} style={{ flex: 1, minHeight: 42 }} />
        <Btn title="Change" kind="ghost" onPress={() => setOther(!other)} style={{ flex: 1, minHeight: 42 }} />
      </Row>
      {other ? <Wrap style={{ marginTop: 8 }}>{Object.entries(CAUSE).filter(([k]) => k !== top.type).map(([k, v]) => <Chip key={k} label={v.label} onPress={() => send('override', k)} />)}</Wrap> : null}
    </View>
  );
}

export default function StudentDetail({ params }: { params: any }) {
  const nav = useNav();
  const { id, subject, name } = params;
  const { data: d, error, loading, reload } = useLoad<any>(() => api('/teacher/student', { params: { student_id: id, subject } }));
  return (
    <Screen title={name} subtitle={d ? `Roll ${d.student.roll_no} · section ${d.student.section}` : undefined} tabs="teacher">
      {loading ? <Loading /> : error ? <ErrorBox message={error} onRetry={reload} /> : (
        <>
          <Card>
            <Row><LevelBadge level={d.level} big /></Row>
            {d.baseline_score != null ? <LevelMeter score={d.baseline_score} secure={d.thresholds.secure} developing={d.thresholds.developing} /> : <Muted>Diagnostic not finished.</Muted>}
            {d.student.progress?.current_chapter ? <Muted>Student says the class is at: {d.student.progress.current_chapter}{d.student.progress.topic_reached ? ` · ${d.student.progress.topic_reached}` : ''}</Muted> : null}
          </Card>
          {d.flags.length ? <Notice tone="warn" icon="flag" text={d.flags.map((x: any) => clean(x.text)).join(' ')} /> : null}
          <Row style={{ alignItems: 'flex-start' }}>
            <View style={{ flex: 1 }}><H>Strengths</H>{d.strengths.length ? d.strengths.map((s: string) => <Muted key={s}>• {s}</Muted>) : <Muted>None yet</Muted>}</View>
            <View style={{ flex: 1 }}><H>Weaknesses</H>{d.weaknesses.length ? d.weaknesses.map((s: string) => <Muted key={s}>• {s}</Muted>) : <Muted>None found</Muted>}</View>
          </Row>
          <H>Why the system thinks so</H>
          {d.concepts.filter((c: any) => c.status !== 'no_evidence' || c.causes.length).map((c: any) => (
            <Card key={c.id}>
              <Row><Text style={{ flex: 1, fontWeight: '800', color: C.ink }}>{c.name}</Text><StatusPill status={c.status} small /></Row>
              <Bar value={c.score ?? 0} color={STATUS[c.status].color} label={`${c.n} answers`} right={c.score != null ? `score ${c.score}` : ''} />
              {c.causes.length ? (
                <View style={{ marginTop: 8 }}>
                  <Muted>Suggested cause:</Muted>
                  <CausePill type={c.causes[0].type} />
                  {c.causes[0].evidence.map((e: string, i: number) => <Muted key={i} style={{ marginTop: 4 }}>• {clean(e)}</Muted>)}
                  {c.status !== 'secure' ? <Review c={c} sid={id} subject={subject} done={reload} /> : null}
                </View>
              ) : null}
            </Card>
          ))}
          <H>Last answers</H>
          <Card>
            {d.history.length === 0 ? <Muted>No answers yet.</Muted> : d.history.slice().reverse().map((h: any, i: number) => (
              <Muted key={i}>{h.correct ? '✓' : '✗'} {h.concept} · {h.difficulty} · {h.time_s}s{h.hint ? ` · hint ×${h.hint}` : ''}{h.support ? ` · ${h.support}` : ''}</Muted>
            ))}
          </Card>
        </>
      )}
    </Screen>
  );
}
