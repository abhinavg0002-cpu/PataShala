import React from 'react';
import { Text, View } from 'react-native';
import { api } from '../api';
import { useNav } from '../nav';
import { C, CAUSE, LEVEL, STATUS } from '../theme';
import { clean } from '../trace';
import { Bar, Btn, Card, CausePill, Donut, ErrorBox, H, Icon, LevelBadge, LevelMeter, Loading, Muted, Notice, Row, Screen, StatusPill, useLoad } from '../ui';

// Used twice: right after the diagnostic ("Result", reveal) and later from the subject page ("Report").
export function ReportView({ subject, name, reveal }: { subject: string; name: string; reveal?: boolean }) {
  const nav = useNav();
  const { data: r, error, loading, reload } = useLoad<any>(() => api('/student/report', { params: { subject } }), [subject]);
  return (
    <Screen title={reveal ? 'Your level' : 'My report'} subtitle={name} onBack={reveal ? () => nav.reset('StudentHome') : undefined} tabs={reveal ? undefined : 'student'} tall
      footer={reveal && r ? <Btn title="Start my learning plan" icon="rocket" onPress={() => nav.replace('Practice', { subject, name })} /> : undefined}>
      {loading ? <Loading text="Working out your level…" /> : error ? <ErrorBox message={error} onRetry={reload} /> : (
        <>
          <Card>
            <Row><LevelBadge level={r.level} big /><Muted style={{ flex: 1 }}>{r.level ? LEVEL[r.level].blurb : 'Keep answering to find your level.'}</Muted></Row>
            {r.baseline_score != null ? (
              <>
                <LevelMeter score={r.baseline_score} secure={r.thresholds.secure} developing={r.thresholds.developing} />
                <Muted>Weighted score {r.baseline_score}. Hard questions count {r.thresholds.weights.hard}×, medium {r.thresholds.weights.medium}×, easy {r.thresholds.weights.easy}×.</Muted>
              </>
            ) : null}
          </Card>
          <Card>
            <Row gap={16}>
              <Donut size={96} center={`${r.counts.secure}/${r.counts.secure + r.counts.developing + r.counts.needs_support}`} caption="secure"
                segments={[{ value: r.counts.secure, color: C.green }, { value: r.counts.developing, color: C.blue }, { value: r.counts.needs_support, color: C.orange }]} />
              <View style={{ flex: 1 }}>
                <Text style={{ fontWeight: '800', color: C.ink, fontSize: 15, marginBottom: 4 }}>Chapter at a glance</Text>
                <Muted>{r.counts.secure} secure · {r.counts.developing} developing · {r.counts.needs_support} need support</Muted>
              </View>
            </Row>
          </Card>
          {r.language.flag ? (
            <Card accent={C.primary2}>
              <Row><CausePill type="language" /></Row>
              <Text style={{ color: C.ink, marginTop: 6 }}>{CAUSE.language.student}</Text>
            </Card>
          ) : null}
          <H>Concept by concept</H>
          {r.concepts.filter((c: any) => c.main || c.status !== 'no_evidence').map((c: any) => (
            <Card key={c.id}>
              <Row><Text style={{ flex: 1, fontWeight: '800', color: C.ink }}>{c.name}</Text><StatusPill status={c.status} small /></Row>
              <View style={{ marginTop: 8 }}>
                <Bar value={c.score ?? 0} color={STATUS[c.status].color} label={c.subtopic + (c.main ? '' : ' · earlier skill')} right={c.n ? `${c.n} answers` : 'not tested'} />
              </View>
              {c.causes.slice(0, 1).map((x: any, i: number) => (
                <View key={i} style={{ marginTop: 6 }}>
                  <CausePill type={x.type} />
                  <Muted style={{ marginTop: 4 }}>{clean(CAUSE[x.type].student)}{x.prereq_name ? ` (${x.prereq_name})` : ''}{x.fix ? ` ${x.fix}` : ''}</Muted>
                </View>
              ))}
            </Card>
          ))}
          {r.what_helped.length ? (
            <>
              <H>What helped you</H>
              {r.what_helped.map((h: any) => <Muted key={h.support}>• {({ simplified: 'Plain wording', example: 'Worked example', recap: 'Earlier-skill recap', contrast: 'Contrast example', hint: 'Hints' } as any)[h.support] ?? h.support}: {h.correct} of {h.tries} right afterwards</Muted>)}
            </>
          ) : null}
          <Notice icon="school" text="Your teacher sees this report once they approve your request." />
        </>
      )}
    </Screen>
  );
}
export default function Report({ params }: { params: any }) { return <ReportView subject={params.subject} name={params.name} />; }
