import React, { useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { api } from '../api';
import { useNav } from '../nav';
import { C, CAUSE } from '../theme';
import { Bar, Btn, Card, Chip, CausePill, ErrorBox, H, Icon, LevelBadge, Loading, Muted, Notice, Row, Screen, Tag, Wrap, useLoad } from '../ui';

const FILTERS = ['All', 'Basic', 'Medium', 'Strong', 'Not tested'];

export default function Roster({ params }: { params: any }) {
  const nav = useNav();
  const { data: r, error, loading, reload } = useLoad<any>(() => api('/teacher/roster', { params: { assignment_id: params.id } }));
  const [filter, setFilter] = useState('All');
  const [sel, setSel] = useState<number[]>([]);
  const [group, setGroup] = useState<any>(null);
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');
  const subject = r?.assignment.subject;
  const rows = (r?.students ?? []).filter((s: any) => filter === 'All' || (s.level ?? 'Not tested') === filter);
  const toggle = (id: number) => { setGroup(null); setMsg(''); setSel(sel.includes(id) ? sel.filter((x) => x !== id) : [...sel, id]); };
  const look = async () => {
    setErr('');
    try { setGroup(await api('/teacher/group', { body: { subject, student_ids: sel } })); } catch (e: any) { setErr(e.message); }
  };
  const assign = async (cid: string) => {
    setErr('');
    try { const x = await api('/teacher/assign', { body: { subject, concept_id: cid, student_ids: sel, note: 'From my teacher' } }); setMsg(`Assigned to ${x.assigned} students. It shows up as their next step.`); } catch (e: any) { setErr(e.message); }
  };
  return (
    <Screen title={params.title} subtitle="Select students to compare and assign work" tabs="teacher">
      {loading ? <Loading /> : error ? <ErrorBox message={error} onRetry={reload} /> : (
        <>
          {r.students.length ? (
            <Card>
              <Text style={{ fontWeight: '800', color: C.ink, marginBottom: 8 }}>Concept gaps in this class</Text>
              {r.concepts.filter((c: any) => c.main).map((c: any) => {
                const n = r.students.filter((s: any) => s.statuses[c.id] === 'needs_support').length;
                return <Bar key={c.id} value={n / r.students.length} color={n ? C.orange : C.green} label={c.name} right={`${n} of ${r.students.length} need support`} />;
              })}
            </Card>
          ) : null}
          <Wrap style={{ marginBottom: 10 }}>{FILTERS.map((f) => <Chip key={f} label={f} selected={filter === f} onPress={() => setFilter(f)} />)}</Wrap>
          <Row style={{ marginBottom: 8 }}>
            <Btn title={sel.length === rows.length && rows.length ? 'Clear' : 'Select all shown'} kind="soft" onPress={() => { setGroup(null); setSel(sel.length === rows.length ? [] : rows.map((s: any) => s.id)); }} style={{ minHeight: 40 }} />
            <Btn title={`Group view (${sel.length})`} icon="people" disabled={!sel.length} onPress={look} style={{ minHeight: 40, flex: 1 }} />
          </Row>
          {err ? <ErrorBox message={err} /> : null}
          {group ? (
            <Card accent={C.primary}>
              <Text style={{ fontWeight: '800', color: C.ink }}>{group.count} students selected</Text>
              {group.shared_weak.length === 0 ? <Muted>No shared weak concepts.</Muted> : (
                <>
                  <Muted style={{ marginVertical: 4 }}>Shared weak concepts. Tap one to assign it to all selected students:</Muted>
                  {group.shared_weak.map((w: any) => <Btn key={w.concept_id} kind="ghost" title={`${w.concept} · ${w.students} of ${group.count}`} onPress={() => assign(w.concept_id)} style={{ marginBottom: 6, minHeight: 42 }} />)}
                </>
              )}
              {group.causes.length ? <Wrap style={{ marginTop: 6 }}>{group.causes.map((c: any) => <Tag key={c.label} text={`${c.label}: ${c.count}`} />)}</Wrap> : null}
              {msg ? <Notice icon="checkmark-circle" text={msg} /> : null}
            </Card>
          ) : null}
          {rows.length === 0 ? <Muted>No students here yet.</Muted> : rows.map((s: any) => {
            const on = sel.includes(s.id);
            return (
              <Card key={s.id} style={{ borderColor: on ? C.primary : C.line, borderWidth: on ? 2 : 1 }}>
                <Row gap={10}>
                  <Pressable onPress={() => toggle(s.id)} accessibilityLabel={`Select ${s.name}`} hitSlop={8}><Icon name={on ? 'checkbox' : 'square-outline'} size={26} color={on ? C.primary : C.mute} /></Pressable>
                  <Pressable style={{ flex: 1 }} onPress={() => nav.push('StudentDetail', { id: s.id, subject, name: s.name })}>
                    <Text style={{ fontWeight: '800', color: C.ink, fontSize: 15 }}>{s.name} <Text style={{ fontWeight: '400', color: C.sub }}>· roll {s.roll_no}</Text></Text>
                    <Row style={{ marginTop: 4, flexWrap: 'wrap' }}>
                      <LevelBadge level={s.level} />
                      {s.primary ? <CausePill type={s.primary.type} /> : null}
                    </Row>
                    {s.weak.length ? <Muted style={{ marginTop: 4 }}>Weak: {s.weak.join(', ')}</Muted> : null}
                    {s.strong.length ? <Muted>Strong: {s.strong.join(', ')}</Muted> : null}
                  </Pressable>
                  <Icon name="chevron-forward" color={C.mute} />
                </Row>
              </Card>
            );
          })}
        </>
      )}
    </Screen>
  );
}
