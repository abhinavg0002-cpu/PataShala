import React from 'react';
import { Text, View } from 'react-native';
import { api } from '../api';
import { DecisionTrace } from '../trace';
import { C, STATUS } from '../theme';
import { Card, ErrorBox, Icon, Loading, Muted, Notice, Row, Screen, Tag, useLoad, useTabs } from '../ui';

export default function Replay() {
  const tabs = useTabs();
  const { data: d, error, loading, reload } = useLoad<any>(() => api('/demo/replay'));
  return (
    <Screen title="Three students, one question" subtitle="Same question, three different next steps" tabs={tabs}>
      {loading ? <Loading /> : error ? <ErrorBox message={error} onRetry={reload} /> : (
        <>
          <Card accent={C.primary}>
            <Muted>{d.question.concept} · {d.question.difficulty}</Muted>
            <Text style={{ fontSize: 17, fontWeight: '700', color: C.ink, marginTop: 4 }}>{d.question.text}</Text>
            {d.question.options.map((o: string, i: number) => <Muted key={i}>{'ABCD'[i]}. {o}</Muted>)}
          </Card>
          {d.students.map((s: any) => (
            <View key={s.role}>
              <Row style={{ marginTop: 6 }}>
                <Icon name="person-circle" size={26} color={C.primary} />
                <Text style={{ fontWeight: '800', color: C.ink, fontSize: 16, flex: 1 }}>{s.label}</Text>
                <Tag text={s.correct ? 'Correct' : 'Wrong'} color={s.correct ? C.green : C.red} bg={s.correct ? C.greenBg : C.redBg} />
              </Row>
              <Muted style={{ marginVertical: 4 }}>Chose: {s.chosen_text}{s.tag_label ? ` (${s.tag_label})` : ''}</Muted>
              <Row style={{ marginBottom: 8 }}>
                <Tag text={STATUS[s.before].label} color={STATUS[s.before].color} bg={STATUS[s.before].bg} /><Icon name="arrow-forward" size={14} color={C.sub} />
                <Tag text={STATUS[s.after].label} color={STATUS[s.after].color} bg={STATUS[s.after].bg} />
              </Row>
              <DecisionTrace trace={s.next.trace} next={{ stage: s.next.stage, concept_name: s.next.concept, question: s.next.difficulty ? { difficulty: s.next.difficulty } : null, support: s.next.support, lesson: s.next.lesson }} />
            </View>
          ))}
          <Notice icon="information-circle" text="Each student gets a different next step because their answers and history differ. The steps are chosen by the same engine every student uses." />
        </>
      )}
    </Screen>
  );
}
