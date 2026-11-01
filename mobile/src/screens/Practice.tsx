import React, { useEffect, useRef, useState } from 'react';
import { Animated, Pressable, Text, View } from 'react-native';
import { api } from '../api';
import { useNav } from '../nav';
import { DecisionTrace } from '../trace';
import { C, DIFF, R, STATUS } from '../theme';
import { Bar, Btn, Card, ErrorBox, Icon, Loading, Muted, Notice, Row, Screen, Tag } from '../ui';

const STAGES = ['Diagnostic', 'Learn', 'Solve', 'Test'];

// One answer option: springs slightly when tapped and changes colour smoothly once marked.
function Option({ letter, text, state, onPress, disabled }: { letter: string; text: string; state: 'idle' | 'selected' | 'right' | 'wrong' | 'dim'; onPress: () => void; disabled: boolean }) {
  const s = useRef(new Animated.Value(1)).current;
  const press = () => { Animated.sequence([Animated.timing(s, { toValue: 0.97, duration: 70, useNativeDriver: true }), Animated.spring(s, { toValue: 1, friction: 4, useNativeDriver: true })]).start(); onPress(); };
  const look = {
    idle: { b: C.line, bg: '#fff', fg: C.ink }, selected: { b: C.teal, bg: C.tealBg, fg: C.ink }, right: { b: C.green, bg: C.greenBg, fg: C.ink },
    wrong: { b: C.red, bg: C.redBg, fg: C.ink }, dim: { b: C.line, bg: '#fff', fg: C.mute },
  }[state];
  return (
    <Animated.View style={{ transform: [{ scale: s }] }}>
      <Pressable onPress={press} disabled={disabled} accessibilityRole="radio" accessibilityState={{ selected: state === 'selected' }}
        style={{ flexDirection: 'row', gap: 12, alignItems: 'center', padding: 14, borderRadius: R.m, marginBottom: 10, borderWidth: 2, borderColor: look.b, backgroundColor: look.bg }}>
        <View style={{ width: 30, height: 30, borderRadius: 15, alignItems: 'center', justifyContent: 'center', backgroundColor: state === 'selected' ? C.teal : state === 'right' ? C.green : state === 'wrong' ? C.red : C.greyBg }}>
          <Text style={{ fontWeight: '800', color: state === 'idle' || state === 'dim' ? C.sub : '#fff' }}>{letter}</Text>
        </View>
        <Text style={{ flex: 1, fontSize: 16, color: look.fg, lineHeight: 22 }}>{text}</Text>
        {state === 'right' ? <Icon name="checkmark-circle" color={C.green} size={22} /> : state === 'wrong' ? <Icon name="close-circle" color={C.red} size={22} /> : null}
      </Pressable>
    </Animated.View>
  );
}

// Fades and slides its children in when it appears (used for feedback).
function Reveal({ children }: { children: React.ReactNode }) {
  const v = useRef(new Animated.Value(0)).current;
  useEffect(() => { Animated.timing(v, { toValue: 1, duration: 280, useNativeDriver: true }).start(); }, [v]);
  return <Animated.View style={{ opacity: v, transform: [{ translateY: v.interpolate({ inputRange: [0, 1], outputRange: [10, 0] }) }] }}>{children}</Animated.View>;
}

function Lesson({ lesson }: { lesson: any }) {
  return (
    <Card accent={C.teal}>
      <Row><Icon name="school" color={C.teal} /><Text style={{ fontWeight: '800', color: C.ink, fontSize: 16 }}>Key ideas</Text></Row>
      {lesson.points.map((p: string, i: number) => <Row key={i} style={{ alignItems: 'flex-start', marginTop: 8 }}><Icon name="checkmark-circle" size={18} color={C.teal} /><Text style={{ flex: 1, color: C.ink, lineHeight: 21, fontSize: 15 }}>{p}</Text></Row>)}
      {lesson.example ? (
        <View style={{ backgroundColor: C.tealBg, borderRadius: R.s, padding: 12, marginTop: 12 }}>
          <Text style={{ fontWeight: '800', color: C.teal }}>Worked example</Text>
          <Text style={{ color: C.ink, marginTop: 4 }}>{lesson.example.q}</Text>
          {lesson.example.steps.map((s: string, i: number) => <Muted key={i}>{s}</Muted>)}
        </View>
      ) : null}
      {lesson.contrast ? (
        <View style={{ backgroundColor: C.redBg, borderRadius: R.s, padding: 10, marginTop: 10 }}>
          <Text style={{ fontWeight: '800', color: C.red }}>Common mistake: {lesson.contrast.label}</Text>
          <Text style={{ color: C.ink, marginTop: 4 }}>{lesson.contrast.fix}</Text>
        </View>
      ) : null}
    </Card>
  );
}

export default function Practice({ params }: { params: any }) {
  const nav = useNav();
  const { subject, name } = params;
  const [step, setStep] = useState<any>(null);
  const [err, setErr] = useState('');
  const [chosen, setChosen] = useState<number | null>(null);
  const [hints, setHints] = useState(0);
  const [res, setRes] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const t0 = useRef(Date.now());

  const load = () => {
    setErr(''); setChosen(null); setHints(0); setRes(null);
    api('/student/next', { params: { subject } }).then((s) => { setStep(s); t0.current = Date.now(); }).catch((e) => setErr(e.message));
  };
  useEffect(load, []);

  const submit = async () => {
    if (chosen == null) return;
    setBusy(true);
    try {
      const r = await api('/student/answer', { body: { subject, question_id: step.question.id, chosen, time_ms: Math.min(Date.now() - t0.current, 600000), hint: hints, support: step.support } });
      setRes(r);
    } catch (e: any) { setErr(e.message); }
    setBusy(false);
  };

  const next = () => {
    if (step.phase === 'diagnostic' && res.next.phase !== 'diagnostic') return nav.replace('Result', { subject, name });
    setStep(res.next); setRes(null); setChosen(null); setHints(0); t0.current = Date.now();
  };

  if (err) return <Screen title={name} onBack={nav.pop}><ErrorBox message={err} onRetry={load} /></Screen>;
  if (!step) return <Screen title={name} onBack={nav.pop}><Loading /></Screen>;
  if (step.phase === 'complete' && !res) {
    return (
      <Screen title="Chapter complete" onBack={nav.pop}>
        <DecisionTrace trace={step.trace} next={step} open />
        <Btn title="See my report" icon="stats-chart" onPress={() => nav.replace('Report', { subject, name })} />
      </Screen>
    );
  }

  const q = step.question;
  const fb = res?.feedback;
  const stageIdx = STAGES.indexOf(step.stage);
  return (
    <Screen title={step.stage} subtitle={`${step.concept_name} · question ${step.progress.answered + 1}`} onBack={nav.pop}
      footer={res ? (
        <Btn title="Next" icon="arrow-forward" onPress={next} />
      ) : <Btn title="Check answer" disabled={chosen == null} loading={busy} onPress={submit} />}>
      <Row style={{ marginBottom: 12, flexWrap: 'wrap' }}>
        {STAGES.map((s, i) => <Tag key={s} text={s} color={i === stageIdx ? '#fff' : C.sub} bg={i === stageIdx ? C.primary : C.greyBg} />)}
      </Row>
      <Row style={{ marginBottom: 10 }}>
        <Tag text={DIFF[q.difficulty].label} color={DIFF[q.difficulty].color} bg={DIFF[q.difficulty].bg} />
        {step.phase === 'diagnostic' ? <Tag text="Finding your level" icon="compass" /> : null}
      </Row>
      {step.lesson && !res ? <Lesson lesson={step.lesson} /> : null}
      {step.support === 'simplified' && !res ? <Notice icon="text" text="Plain wording: same question, simpler words." /> : null}
      <Card>
        <Text style={{ fontSize: 18, fontWeight: '700', color: C.ink, lineHeight: 26 }}>{q.text}</Text>
        <View style={{ height: 12 }} />
        {q.options.map((o: string, i: number) => {
          const state = fb ? (i === fb.answer ? 'right' : chosen === i ? 'wrong' : 'dim') : chosen === i ? 'selected' : 'idle';
          return <Option key={i} letter={'ABCD'[i]} text={o} state={state as any} disabled={!!res} onPress={() => setChosen(i)} />;
        })}
        {!res ? (
          <>
            {q.hints.slice(0, hints).map((h: string, i: number) => <Reveal key={i}><Row style={{ alignItems: 'flex-start', backgroundColor: C.amberBg, padding: 10, borderRadius: R.s, marginBottom: 8 }}><Icon name="bulb" size={18} color={C.amberText} /><Text style={{ flex: 1, color: C.amberText, lineHeight: 20 }}><Text style={{ fontWeight: '800' }}>Hint {i + 1}  </Text>{h}</Text></Row></Reveal>)}
            {hints < 3 ? <Btn title={`Show hint ${hints + 1}`} kind="soft" icon="bulb" onPress={() => setHints(hints + 1)} /> : null}
            {hints > 0 ? <Muted style={{ marginTop: 6 }}>A correct answer with a hint counts as half.</Muted> : null}
          </>
        ) : null}
      </Card>
      {res ? (
        <Reveal>
          <Card accent={fb.correct ? C.green : C.red}>
            <Row><Icon name={fb.correct ? 'checkmark-circle' : 'close-circle'} color={fb.correct ? C.green : C.red} size={24} />
              <Text style={{ fontWeight: '800', color: fb.correct ? C.green : C.red, fontSize: 17 }}>{fb.correct ? 'Correct' : 'Not quite'}</Text></Row>
            {!fb.correct ? <Text style={{ marginTop: 8, color: C.ink, fontSize: 15 }}>Correct answer: <Text style={{ fontWeight: '800' }}>{fb.answer_text}</Text></Text> : null}
            <View style={{ backgroundColor: C.bg, borderRadius: R.s, padding: 10, marginTop: 10 }}>
              <Text style={{ fontWeight: '800', color: C.primary, marginBottom: 2 }}>Explanation</Text>
              <Text style={{ color: C.ink, lineHeight: 21 }}>{fb.why}</Text>
            </View>
            {fb.tag_label ? <Notice tone="warn" icon="bulb" text={`${fb.tag_label}: ${fb.fix}`} /> : null}
            <Row style={{ marginTop: 10, flexWrap: 'wrap' }}>
              <Text style={{ color: C.sub, fontSize: 12 }}>{res.concept.name}:</Text>
              <Tag text={STATUS[res.concept.before].label} color={STATUS[res.concept.before].color} bg={STATUS[res.concept.before].bg} />
              <Icon name="arrow-forward" size={14} color={C.sub} />
              <Tag text={STATUS[res.concept.after].label} color={STATUS[res.concept.after].color} bg={STATUS[res.concept.after].bg} />
            </Row>
          </Card>
          <DecisionTrace trace={res.next.trace} next={res.next} />
        </Reveal>
      ) : null}
    </Screen>
  );
}
