import React from 'react';
import { Text, View } from 'react-native';
import { api } from '../api';
import { useNav } from '../nav';
import { C, SUBJECT_ICON } from '../theme';
import { Card, Donut, ErrorBox, H, Icon, LevelBadge, Loading, Muted, Row, Screen, useLoad } from '../ui';

// One donut per subject: how many concepts are secure, developing or need support.
export default function Progress() {
  const nav = useNav();
  const { data, error, loading, reload } = useLoad<any[]>(() => api('/student/subjects'));
  const subjects = (data ?? []).filter((s) => s.enabled);
  return (
    <Screen title="My progress" subtitle="Concept mastery in each subject" tabs="student">
      {loading ? <Loading /> : error ? <ErrorBox message={error} onRetry={reload} /> : subjects.map((s) => {
        const c = s.counts, n = c.secure + c.developing + c.needs_support;
        return (
          <Card key={s.id} onPress={s.answered > 0 ? () => nav.push('Report', { subject: s.id, name: s.name }) : undefined}>
            <Row gap={16}>
              <Donut size={104} center={n ? `${c.secure}/${n}` : '–'} caption="secure"
                segments={[{ value: c.secure, color: C.green }, { value: c.developing, color: C.blue }, { value: c.needs_support, color: C.orange }]} />
              <View style={{ flex: 1, gap: 4 }}>
                <Row><Icon name={SUBJECT_ICON[s.id] ?? 'book'} color={C.teal} size={18} /><Text style={{ fontWeight: '800', color: C.ink, fontSize: 16, flex: 1 }}>{s.name}</Text></Row>
                <LevelBadge level={s.level} />
                {n ? (
                  <>
                    <Row><View style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: C.green }} /><Muted>{c.secure} secure</Muted></Row>
                    <Row><View style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: C.blue }} /><Muted>{c.developing} developing</Muted></Row>
                    <Row><View style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: C.orange }} /><Muted>{c.needs_support} need support</Muted></Row>
                  </>
                ) : <Muted>No answers yet</Muted>}
              </View>
              {s.answered > 0 ? <Icon name="chevron-forward" color={C.mute} /> : null}
            </Row>
          </Card>
        );
      })}
      <H>Reading the chart</H>
      <Muted>Each ring shows the main concepts of the chapter. Tap a subject for the full report.</Muted>
    </Screen>
  );
}
