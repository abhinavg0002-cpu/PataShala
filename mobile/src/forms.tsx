import React, { useEffect, useState } from 'react';
import { View } from 'react-native';
import { api, getCatalog } from './api';
import { C } from './theme';
import { Choice, Chip, ErrorBox, Field, H, Icon, Loading, Muted, Notice, Row, T, Wrap } from './ui';

// ---------------------------------------------------------------- school + branch
// The user types the school and the branch; matching names appear below the box and one must be tapped to confirm it.
function Typeahead({ label, placeholder, items, selectedId, onPick, onClear, empty }: { label: string; placeholder: string; items: { id: number; name: string }[]; selectedId: number | null; onPick: (id: number) => void; onClear: () => void; empty: string }) {
  const [text, setText] = useState('');
  const chosen = items.find((i) => i.id === selectedId);
  const q = text.trim().toLowerCase();
  const matches = q && !chosen ? items.filter((i) => i.name.toLowerCase().includes(q)).slice(0, 5) : [];
  return (
    <View>
      <Field label={label} value={chosen ? chosen.name : text} placeholder={placeholder} autoCap="words"
        onChangeText={(t) => { if (chosen) onClear(); setText(t); }} />
      {chosen ? <Row style={{ marginTop: -6, marginBottom: 10 }}><Icon name="checkmark-circle" size={16} color={C.green} /><Muted>Selected. Edit the text to change it.</Muted></Row> : null}
      {matches.map((m) => <Choice key={m.id} title={m.name} icon="business" onPress={() => { onPick(m.id); setText(m.name); }} />)}
      {q && !chosen && matches.length === 0 ? <Muted style={{ marginBottom: 10 }}>{empty}</Muted> : null}
    </View>
  );
}

export function SchoolPicker({ school, branch, onChange }: { school: number | null; branch: number | null; onChange: (s: number | null, b: number | null) => void }) {
  const [list, setList] = useState<any[] | null>(null);
  const [err, setErr] = useState('');
  useEffect(() => { api('/schools').then(setList).catch((e) => setErr(e.message)); }, []);
  if (err) return <ErrorBox message={err} />;
  if (!list) return <Loading />;
  const chosen = list.find((s) => s.id === school);
  return (
    <View>
      <Typeahead label="School name" placeholder="Start typing your school's name" items={list} selectedId={school}
        onPick={(id) => onChange(id, null)} onClear={() => onChange(null, null)} empty="No school found with that name. Check the spelling." />
      {chosen ? (
        <Typeahead key={chosen.id} label="Branch" placeholder="Type your branch name" items={chosen.branches} selectedId={branch}
          onPick={(id) => onChange(school, id)} onClear={() => onChange(school, null)} empty="No branch found with that name at this school." />
      ) : null}
    </View>
  );
}

// ---------------------------------------------------------------- academic year and chapter progress
export type Prog = { year_status: 'starting' | 'ongoing' | ''; chapters_done: string[]; current_chapter: string | null; topic_reached: string | null };
export const emptyProg = (): Prog => ({ year_status: '', chapters_done: [], current_chapter: null, topic_reached: null });

export function ProgressForm({ items, values, onChange }: { items: { key: string; subject: string; title: string; sub?: string; enabled?: boolean }[]; values: Record<string, Prog>; onChange: (v: Record<string, Prog>) => void }) {
  const [cat, setCat] = useState<any>(null);
  const [active, setActive] = useState(items.find((i) => i.enabled !== false)?.key ?? items[0]?.key);
  useEffect(() => { getCatalog().then(setCat); }, []);
  if (!cat) return <Loading />;
  const item = items.find((i) => i.key === active) ?? items[0];
  const subj = item.subject;
  const p: Prog = values[item.key] ?? emptyProg();
  const set = (patch: Partial<Prog>) => onChange({ ...values, [item.key]: { ...p, ...patch } });
  const chapters: any[] = cat.chapters[subj] ?? [];
  const demo = cat.demo_chapter[subj];
  const subtopics: string[] = cat.subtopics[subj] ?? [];
  const todo = items.filter((i) => i.enabled !== false && !values[i.key]?.year_status);
  return (
    <View>
      {items.length > 1 ? <Wrap style={{ marginBottom: 12 }}>{items.map((i) => <Chip key={i.key} label={i.title} locked={i.enabled === false} icon={values[i.key]?.year_status ? 'checkmark-circle' : undefined} selected={i.key === item.key} onPress={() => setActive(i.key)} />)}</Wrap> : null}
      <Row style={{ marginBottom: 8 }}><Icon name="book" color={C.primary} /><T bold style={{ flex: 1 }}>{item.title}{item.sub ? ` · ${item.sub}` : ''}</T></Row>
      <Choice title={cat.book} icon="library" sub="State textbook" />
      <H>Academic year</H>
      <Wrap>
        <Chip label="Just starting" selected={p.year_status === 'starting'} onPress={() => set({ year_status: 'starting', chapters_done: [], current_chapter: null, topic_reached: null })} icon="flag" />
        <Chip label="Already started" selected={p.year_status === 'ongoing'} onPress={() => set({ year_status: 'ongoing' })} icon="play" />
      </Wrap>
      {p.year_status === 'ongoing' ? (
        <>
          <H>Chapters completed</H>
          <Muted style={{ marginBottom: 6 }}>Tick every chapter that is finished.</Muted>
          {chapters.filter((c) => c.title !== demo).map((c) => {
            const on = p.chapters_done.includes(c.title);
            return <Choice key={c.title} title={`${c.no ? `Ch ${c.no} · ` : ''}${c.title}`} selected={on} icon="checkbox-outline" onPress={() => set({ chapters_done: on ? p.chapters_done.filter((x) => x !== c.title) : [...p.chapters_done, c.title] })} />;
          })}
          <H>Chapter being taught now</H>
          <Choice title={`${chapters.find((c) => c.title === demo)?.no ? `Ch ${chapters.find((c) => c.title === demo).no} · ` : ''}${demo}`} icon="bookmark" selected={p.current_chapter === demo} sub="Chapter in progress" onPress={() => set({ current_chapter: demo })} />
          {chapters.filter((c) => c.title !== demo).slice(0, 2).map((c) => <Choice key={c.title} title={c.title} locked icon="bookmark" />)}
          {p.current_chapter === demo ? (
            <>
              <H>Topic reached so far</H>
              <Wrap>
                <Chip label="Not started" selected={p.topic_reached === 'Not started'} onPress={() => set({ topic_reached: 'Not started' })} />
                {subtopics.map((s) => <Chip key={s} label={s} selected={p.topic_reached === s} onPress={() => set({ topic_reached: s })} />)}
              </Wrap>
            </>
          ) : null}
        </>
      ) : p.year_status === 'starting' ? (
        <Notice text={`Starting fresh: we will begin with "${demo}".`} />
      ) : null}
      {todo.length ? <Notice tone="warn" icon="alert-circle" text={`Still to choose: ${todo.map((i) => i.title).join(', ')}. Tap each subject above and pick Just starting or Already started.`} /> : null}
    </View>
  );
}

export const progressDone = (keys: string[], v: Record<string, Prog>) => keys.every((k) => v[k]?.year_status);
