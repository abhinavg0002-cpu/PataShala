import React from 'react';
import { Text, View } from 'react-native';
import { C, DIFF, R } from './theme';
import { Collapsible, Icon, Muted, Tag } from './ui';

// Internal rule ids such as "(R8)" are for logs and tests; people never see them.
export const clean = (s: string) => s.replace(/\s*\(R(?:-T|\d+)[^)]*\)/g, '').replace(/\bR(?:-T|\d+)\b:?\s*/g, '').trim();

export type Trace = { rule: string; headline: string; observed: string[]; decision: string; student_text: string; teacher_text: string };

function Node({ n, title, last, children, color = C.primary }: { n: number; title: string; last?: boolean; children: React.ReactNode; color?: string }) {
  return (
    <View style={{ flexDirection: 'row', gap: 10 }}>
      <View style={{ alignItems: 'center', width: 26 }}>
        <View style={{ width: 26, height: 26, borderRadius: 13, backgroundColor: color, alignItems: 'center', justifyContent: 'center' }}>
          <Text style={{ color: '#fff', fontWeight: '800', fontSize: 13 }}>{n}</Text>
        </View>
        {!last ? <View style={{ flex: 1, width: 2, backgroundColor: C.line, marginVertical: 2 }} /> : null}
      </View>
      <View style={{ flex: 1, paddingBottom: last ? 0 : 12 }}>
        <Text style={{ fontWeight: '800', color: C.ink, fontSize: 13, marginBottom: 3 }}>{title}</Text>
        {children}
      </View>
    </View>
  );
}

// "Why this next step?": the proof of how the system decides, shown after every answer.
export function DecisionTrace({ trace, next, audience = 'student', open }: { trace: Trace; next?: any; audience?: 'student' | 'teacher'; open?: boolean }) {
  const say = clean(audience === 'teacher' ? trace.teacher_text : trace.student_text);
  const q = next?.question;
  return (
    <View style={{ backgroundColor: '#fff', borderRadius: R.m, borderWidth: 1.5, borderColor: C.teal, padding: 14, marginBottom: 12 }}>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 6 }}>
        <Icon name="git-network" color={C.teal} size={20} />
        <Text style={{ fontWeight: '800', color: C.teal, fontSize: 15, flex: 1 }}>Why this next step?</Text>
              </View>
      <Text style={{ fontSize: 16, color: C.ink, lineHeight: 22, fontWeight: '600' }}>{say}</Text>
      <View style={{ height: 8 }} />
      <Collapsible title="Show how the system decided" icon="eye" open={open}>
        <Node n={1} title="What we noticed">
          {trace.observed.map((o, i) => <Muted key={i}>• {clean(o)}</Muted>)}
        </Node>
        <Node n={2} title="What we decided" color={C.teal}>
          <Muted>{clean(trace.decision)}</Muted>
        </Node>
        <Node n={3} title="Your next step" last color={C.green}>
          {next?.phase === 'complete' || !q ? <Muted>Chapter finished.</Muted> : (
            <View style={{ gap: 4 }}>
              <Text style={{ fontSize: 13, color: C.ink }}>{next.stage} · {next.concept_name}</Text>
              <View style={{ flexDirection: 'row', gap: 6, flexWrap: 'wrap' }}>
                <Tag text={DIFF[q.difficulty].label} color={DIFF[q.difficulty].color} bg={DIFF[q.difficulty].bg} />
                {next.lesson ? <Tag text="Lesson first" icon="school" /> : null}
                {next.support === 'simplified' ? <Tag text="Plain wording" icon="text" /> : null}
                {next.support === 'example' ? <Tag text="Worked example" icon="reader" /> : null}
                {next.support === 'recap' ? <Tag text="Earlier-skill recap" icon="refresh" /> : null}
                {next.support === 'contrast' ? <Tag text="Contrast example" icon="swap-horizontal" /> : null}
              </View>
            </View>
          )}
        </Node>
        <Muted style={{ marginTop: 8, fontStyle: 'italic' }}>Every step follows clear rules that your teacher can check.</Muted>
      </Collapsible>
    </View>
  );
}
