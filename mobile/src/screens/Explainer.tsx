import React from 'react';
import { Text, View } from 'react-native';
import { api } from '../api';
import { useNav } from '../nav';
import { C, CAUSE, LEVEL } from '../theme';
import { Card, CausePill, H, Icon, LevelBadge, Muted, Row, Screen, Tag, useLoad, useTabs } from '../ui';

const FLOW = [
  ['school', 'Learn', 'Short lesson in plain words'],
  ['create', 'Solve', 'Practice with hints'],
  ['ribbon', 'Test', 'Harder questions to confirm'],
  ['git-network', 'Decide', 'Clear rules pick the next step'],
];

export default function Explainer() {
  const nav = useNav();
  const tabs = useTabs();
  const { data: v } = useLoad<any>(() => api('/demo/validation'));
  return (
    <Screen title="How the system decides" subtitle="Clear rules, not guesses" tabs={tabs}>
      <H>1 · Find the level</H>
      <Card>
        <Muted>A short diagnostic mixes easy, medium and hard questions across the chapter. Harder questions count more.</Muted>
        <View style={{ gap: 8, marginTop: 10 }}>
          {Object.entries(LEVEL).map(([k, l]) => <Row key={k}><LevelBadge level={k} /><Muted style={{ flex: 1 }}>{l.blurb}</Muted></Row>)}
        </View>
      </Card>
      <H>2 · Find the reason</H>
      <Card>
        <Muted style={{ marginBottom: 8 }}>For each weak concept the system checks causes in this order and shows the first one that fits:</Muted>
        {Object.entries(CAUSE).map(([k, c]) => <View key={k} style={{ marginBottom: 8 }}><CausePill type={k} /><Muted style={{ marginTop: 2 }}>{c.student}</Muted></View>)}
      </Card>
      <H>3 · Pick the next step</H>
      <Card>
        <Row style={{ justifyContent: 'space-between' }}>
          {FLOW.map(([ic, t, s]) => (
            <View key={t} style={{ alignItems: 'center', flex: 1 }}>
              <View style={{ width: 40, height: 40, borderRadius: 20, backgroundColor: C.tealBg, alignItems: 'center', justifyContent: 'center' }}><Icon name={ic} color={C.teal} /></View>
              <Text style={{ fontWeight: '800', fontSize: 12, color: C.ink, marginTop: 4 }}>{t}</Text>
              <Text style={{ fontSize: 10, color: C.sub, textAlign: 'center' }}>{s}</Text>
            </View>
          ))}
        </Row>
        <Muted style={{ marginTop: 10 }}>Two right in a row → harder. Wrong twice → an easier step with a worked example. Same wrong idea twice → contrast example. Weak earlier skill → go back to it first.</Muted>
      </Card>
      <H>4 · Teacher stays in control</H>
      <Card><Muted>The teacher sees the suggested cause and can confirm or change it. Only teachers with an approved link to a student can see that student.</Muted></Card>
      <Card onPress={() => nav.push('Replay')} accent={C.teal}>
        <Row><Icon name="people-circle" color={C.teal} size={24} /><View style={{ flex: 1 }}><Text style={{ fontWeight: '800', color: C.ink }}>See it in action</Text><Muted>Three students answer the same question and get three different next steps</Muted></View><Icon name="chevron-forward" color={C.mute} /></Row>
      </Card>
      {v ? (
        <>
          <H>How we check the rules</H>
          <Card>
            <Row><Tag text={`${v.students} simulated learners`} icon="flask" /></Row>
            <Muted style={{ marginTop: 6 }}>Finding weak concepts: the adaptive test scored precision {v.weak_concepts_engine.precision} and recall {v.weak_concepts_engine.recall}, against {v.weak_concepts_fixed10.precision} and {v.weak_concepts_fixed10.recall} for a fixed 10-question test.</Muted>
            <Muted>English reading load found in {v.english_load.engine_flagged} of {v.english_load.students} learners (a fixed test cannot detect this).</Muted>
            <Muted>Strong students wrongly marked weak: {v.strong_students.wrongly_flagged_weak} of {v.strong_students.n}.</Muted>
            <Muted>Main cause matched: {v.cause_primary_matches.matched} of {v.cause_primary_matches.n}.</Muted>
            <Muted style={{ marginTop: 6, fontStyle: 'italic' }}>Simulated learners, not real students.</Muted>
          </Card>
        </>
      ) : null}
    </Screen>
  );
}
