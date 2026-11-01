import { Ionicons } from '@expo/vector-icons';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator, Animated, Platform, Pressable, ScrollView, StyleProp, StyleSheet, Text, TextInput, TextStyle, View, ViewStyle,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Svg, { Circle } from 'react-native-svg';
import { useNav } from './nav';
import { useAuth } from './store';
import { C, CAUSE, LEVEL, R, STATUS } from './theme';

export const Icon = ({ name, size = 20, color = C.ink }: { name: string; size?: number; color?: string }) => (
  <Ionicons name={name as any} size={size} color={color} />
);

// ---------------------------------------------------------------- text
export const T = ({ children, style, size = 15, bold, color = C.ink, center }: { children: React.ReactNode; style?: StyleProp<TextStyle>; size?: number; bold?: boolean; color?: string; center?: boolean }) => (
  <Text style={[{ fontSize: size, color, fontWeight: bold ? '700' : '400', lineHeight: size * 1.4, textAlign: center ? 'center' : 'auto' }, style]}>{children}</Text>
);
export const H = ({ children, style }: { children: React.ReactNode; style?: StyleProp<TextStyle> }) => (
  <Text style={[{ fontSize: 18, fontWeight: '800', color: C.ink, marginTop: 8, marginBottom: 8 }, style]}>{children}</Text>
);
export const Muted = ({ children, style, size = 13 }: { children: React.ReactNode; style?: StyleProp<TextStyle>; size?: number }) => (
  <Text style={[{ fontSize: size, color: C.sub, lineHeight: size * 1.4 }, style]}>{children}</Text>
);

// ---------------------------------------------------------------- layout
const TABS: Record<string, { name: string; label: string; icon: string; also?: string[] }[]> = {
  student: [
    { name: 'StudentHome', label: 'Home', icon: 'home', also: ['SubjectHub', 'Practice', 'Result'] },
    { name: 'Progress', label: 'Progress', icon: 'stats-chart', also: ['Report'] },
    { name: 'Explainer', label: 'How it works', icon: 'compass', also: ['Replay'] },
  ],
  teacher: [
    { name: 'TeacherHome', label: 'Home', icon: 'home', also: ['Roster', 'StudentDetail'] },
    { name: 'Explainer', label: 'How it works', icon: 'compass', also: ['Replay'] },
  ],
};

// Bottom tabs: the current section is highlighted, tapping another section replaces the stack (no back-button pile-up).
export function TabBar({ kind }: { kind: 'student' | 'teacher' }) {
  const nav = useNav();
  const ins = useSafeAreaInsets();
  return (
    <View style={{ flexDirection: 'row', backgroundColor: '#fff', borderTopWidth: 1, borderTopColor: C.line, paddingBottom: Math.max(ins.bottom, 6), paddingTop: 6 }}>
      {TABS[kind].map((t) => {
        const on = nav.route.name === t.name || !!t.also?.includes(nav.route.name);
        return (
          <Pressable key={t.name} onPress={() => (nav.route.name === t.name ? undefined : nav.reset(t.name))} accessibilityRole="tab" accessibilityState={{ selected: on }}
            style={{ flex: 1, alignItems: 'center', paddingVertical: 4, gap: 2 }}>
            <View style={{ paddingHorizontal: 16, paddingVertical: 3, borderRadius: 999, backgroundColor: on ? C.tealBg : 'transparent' }}>
              <Icon name={on ? t.icon : t.icon + '-outline'} size={22} color={on ? C.teal : C.sub} />
            </View>
            <Text style={{ fontSize: 11, fontWeight: on ? '800' : '600', color: on ? C.teal : C.sub }}>{t.label}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

export function Screen({ title, subtitle, onBack, right, children, footer, scroll = true, tall, tabs }: {
  title: string; subtitle?: string; onBack?: () => void; right?: React.ReactNode; children: React.ReactNode; footer?: React.ReactNode; scroll?: boolean; tall?: boolean; tabs?: 'student' | 'teacher';
}) {
  const ins = useSafeAreaInsets();
  const nav = useNav();
  // Every screen that was opened from another one gets the same back arrow; tab roots (reached by reset) have none.
  // Inside a section: back goes to the previous screen. On another tab's first screen: back goes to Home.
  const home = tabs === 'teacher' ? 'TeacherHome' : 'StudentHome';
  const back = onBack ?? (nav.canGoBack ? nav.pop : tabs && nav.route.name !== home ? () => nav.reset(home) : undefined);
  return (
    <View style={{ flex: 1, backgroundColor: C.bg }}>
      <View style={{ backgroundColor: C.primary, paddingTop: ins.top + 12, paddingBottom: tall ? 26 : 16, paddingHorizontal: 16, borderBottomLeftRadius: tall ? 22 : 0, borderBottomRightRadius: tall ? 22 : 0 }}>
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          {back ? (
            <Pressable onPress={back} accessibilityLabel="Go back" hitSlop={8} style={{ marginRight: 10, width: 36, height: 36, borderRadius: 18, backgroundColor: 'rgba(255,255,255,0.12)', alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="arrow-back" color="#fff" size={22} />
            </Pressable>
          ) : null}
          <View style={{ flex: 1 }}>
            <Text style={{ color: '#fff', fontSize: 20, fontWeight: '800' }} numberOfLines={2}>{title}</Text>
            {subtitle ? <Text style={{ color: '#B9C6D6', fontSize: 13, marginTop: 2 }} numberOfLines={2}>{subtitle}</Text> : null}
          </View>
          {right ?? (tabs && nav.route.name !== 'Settings' ? (
            <Pressable onPress={() => nav.push('Settings')} accessibilityLabel="Settings" hitSlop={8}
              style={{ width: 36, height: 36, borderRadius: 18, backgroundColor: 'rgba(255,255,255,0.12)', alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="settings-outline" color="#fff" size={20} />
            </Pressable>
          ) : null)}
        </View>
      </View>
      {scroll ? (
        <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16, paddingBottom: 32 }} keyboardShouldPersistTaps="handled">
          {children}
        </ScrollView>
      ) : (
        <View style={{ flex: 1, padding: 16 }}>{children}</View>
      )}
      {footer ? <View style={{ padding: 12, paddingBottom: 12 + (tabs ? 0 : ins.bottom), backgroundColor: '#fff', borderTopWidth: 1, borderTopColor: C.line }}>{footer}</View> : null}
      {tabs ? <TabBar kind={tabs} /> : null}
    </View>
  );
}

// Which tab bar to show on shared screens (Explainer, Replay): none before login.
export function useTabs(): 'student' | 'teacher' | undefined {
  const { user } = useAuth();
  return user?.role;
}

export const Card = ({ children, style, onPress, accent }: { children: React.ReactNode; style?: StyleProp<ViewStyle>; onPress?: () => void; accent?: string }) => {
  const body = (
    <View style={[{ backgroundColor: C.card, borderRadius: R.m, padding: 14, marginBottom: 12, borderWidth: 1, borderColor: C.line, borderLeftWidth: accent ? 5 : 1, borderLeftColor: accent ?? C.line,
      shadowColor: '#0F172A', shadowOpacity: 0.05, shadowRadius: 8, shadowOffset: { width: 0, height: 2 }, elevation: 1 }, style]}>
      {children}
    </View>
  );
  return onPress ? <Pressable onPress={onPress} style={({ pressed }) => ({ opacity: pressed ? 0.85 : 1 })}>{body}</Pressable> : body;
};

export const Row = ({ children, style, gap = 8 }: { children: React.ReactNode; style?: StyleProp<ViewStyle>; gap?: number }) => (
  <View style={[{ flexDirection: 'row', alignItems: 'center', gap }, style]}>{children}</View>
);
export const Wrap = ({ children, style }: { children: React.ReactNode; style?: StyleProp<ViewStyle> }) => (
  <View style={[{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }, style]}>{children}</View>
);

// ---------------------------------------------------------------- controls
export function Btn({ title, onPress, kind = 'primary', icon, disabled, loading, style }: {
  title: string; onPress?: () => void; kind?: 'primary' | 'ghost' | 'danger' | 'soft'; icon?: string; disabled?: boolean; loading?: boolean; style?: StyleProp<ViewStyle>;
}) {
  const bg = kind === 'primary' ? C.teal : kind === 'danger' ? C.red : kind === 'soft' ? C.tealBg : 'transparent';
  const fg = kind === 'primary' || kind === 'danger' ? '#fff' : C.teal;
  const off = disabled || loading;
  return (
    <Pressable onPress={off ? undefined : onPress} accessibilityRole="button" accessibilityState={{ disabled: !!off }}
      style={({ pressed }) => [{ minHeight: 50, borderRadius: R.m, paddingHorizontal: 18, backgroundColor: bg, alignItems: 'center', justifyContent: 'center', flexDirection: 'row', gap: 8,
        borderWidth: kind === 'ghost' ? 1.5 : 0, borderColor: C.teal, opacity: off ? 0.5 : pressed ? 0.85 : 1 }, style]}>
      {loading ? <ActivityIndicator color={fg} /> : icon ? <Icon name={icon} color={fg} size={20} /> : null}
      <Text style={{ color: fg, fontWeight: '700', fontSize: 16 }}>{title}</Text>
    </Pressable>
  );
}

export function Chip({ label, selected, onPress, locked, icon }: { label: string; selected?: boolean; onPress?: () => void; locked?: boolean; icon?: string }) {
  // "locked" options are catalogue entries that are not wired up: same look as any option, but they do nothing.
  return (
    <Pressable onPress={locked ? undefined : onPress} accessibilityState={{ selected: !!selected }}
      style={{ paddingVertical: 9, paddingHorizontal: 14, borderRadius: 999, borderWidth: 1.5, flexDirection: 'row', alignItems: 'center', gap: 6,
        borderColor: selected ? C.teal : C.line, backgroundColor: selected ? C.teal : '#fff' }}>
      {icon ? <Icon name={icon} size={15} color={selected ? '#fff' : C.teal} /> : null}
      <Text style={{ color: selected ? '#fff' : C.ink, fontWeight: '600', fontSize: 14 }}>{label}</Text>
    </Pressable>
  );
}

// A list row used for boards, states, subjects, schools.
export function Choice({ title, sub, selected, onPress, locked, icon, right }: { title: string; sub?: string; selected?: boolean; onPress?: () => void; locked?: boolean; icon?: string; right?: React.ReactNode }) {
  return (
    <Pressable onPress={locked ? undefined : onPress} accessibilityState={{ selected: !!selected }}
      style={{ flexDirection: 'row', alignItems: 'center', gap: 12, padding: 12, borderRadius: R.m, marginBottom: 8, borderWidth: 1.5,
        borderColor: selected ? C.teal : C.line, backgroundColor: selected ? C.tealBg : '#fff' }}>
      <View style={{ width: 38, height: 38, borderRadius: 19, backgroundColor: selected ? C.teal : C.tealBg, alignItems: 'center', justifyContent: 'center' }}>
        <Icon name={selected ? 'checkmark' : icon ?? 'ellipse-outline'} size={18} color={selected ? '#fff' : C.teal} />
      </View>
      <View style={{ flex: 1 }}>
        <Text style={{ fontSize: 15, fontWeight: '700', color: C.ink }}>{title}</Text>
        {sub ? <Text style={{ fontSize: 12, color: C.sub }}>{sub}</Text> : null}
      </View>
      {right}
    </Pressable>
  );
}

export function Field({ label, value, onChangeText, placeholder, secure, keyboard, maxLength, error, autoCap }: {
  label: string; value: string; onChangeText: (t: string) => void; placeholder?: string; secure?: boolean; keyboard?: 'default' | 'number-pad' | 'url'; maxLength?: number; error?: string; autoCap?: 'none' | 'words' | 'characters';
}) {
  const [show, setShow] = useState(false);
  return (
    <View style={{ marginBottom: 12 }}>
      <Text style={{ fontSize: 13, fontWeight: '700', color: C.sub, marginBottom: 6 }}>{label}</Text>
      <View>
      <TextInput value={value} onChangeText={onChangeText} placeholder={placeholder} placeholderTextColor={C.mute} secureTextEntry={secure && !show}
        keyboardType={keyboard === 'url' ? 'url' : keyboard === 'number-pad' ? 'number-pad' : 'default'} maxLength={maxLength} autoCapitalize={autoCap ?? 'none'} autoCorrect={false}
        accessibilityLabel={label}
        style={{ borderWidth: 1.5, borderColor: error ? C.red : C.line, borderRadius: R.s, paddingHorizontal: 14, paddingRight: secure ? 48 : 14, paddingVertical: Platform.OS === 'ios' ? 14 : 10, fontSize: 16, backgroundColor: '#fff', color: C.ink }} />
      {secure ? <Pressable onPress={() => setShow(!show)} accessibilityLabel={show ? 'Hide PIN' : 'Show PIN'} hitSlop={8} style={{ position: 'absolute', right: 12, top: 0, bottom: 0, justifyContent: 'center' }}><Icon name={show ? 'eye-off' : 'eye'} color={C.sub} /></Pressable> : null}
      </View>
      {error ? <Text style={{ color: C.red, fontSize: 12, marginTop: 4 }}>{error}</Text> : null}
    </View>
  );
}

// ---------------------------------------------------------------- badges
export function StatusPill({ status, small }: { status: string; small?: boolean }) {
  const s = STATUS[status] ?? STATUS.no_evidence;
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: s.bg, paddingHorizontal: small ? 7 : 10, paddingVertical: small ? 3 : 5, borderRadius: 999, alignSelf: 'flex-start' }}>
      <Icon name={s.icon} size={small ? 12 : 14} color={s.color} />
      <Text style={{ color: s.color, fontWeight: '700', fontSize: small ? 11 : 12 }}>{s.label}</Text>
    </View>
  );
}
export function LevelBadge({ level, big }: { level?: string | null; big?: boolean }) {
  const l = level ? LEVEL[level] : null;
  if (!l) return <View style={{ backgroundColor: C.greyBg, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 999 }}><Text style={{ color: C.grey, fontWeight: '700', fontSize: 12 }}>Not tested yet</Text></View>;
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: l.bg, paddingHorizontal: big ? 16 : 10, paddingVertical: big ? 8 : 4, borderRadius: 999, alignSelf: 'flex-start' }}>
      <Icon name={l.icon} size={big ? 20 : 13} color={l.color} />
      <Text style={{ color: l.color, fontWeight: '800', fontSize: big ? 20 : 12 }}>{level}</Text>
    </View>
  );
}
export function CausePill({ type, label }: { type: string; label?: string }) {
  const c = CAUSE[type];
  if (!c) return null;
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 5, backgroundColor: c.bg, paddingHorizontal: 9, paddingVertical: 4, borderRadius: 999, alignSelf: 'flex-start' }}>
      <Icon name={c.icon} size={13} color={c.color} />
      <Text style={{ color: c.color, fontWeight: '700', fontSize: 12 }}>{label ?? c.label}</Text>
    </View>
  );
}
export const Tag = ({ text, color = C.teal, bg = C.tealBg, icon }: { text: string; color?: string; bg?: string; icon?: string }) => (
  <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: bg, paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8, alignSelf: 'flex-start' }}>
    {icon ? <Icon name={icon} size={12} color={color} /> : null}
    <Text style={{ color, fontWeight: '700', fontSize: 11 }}>{text}</Text>
  </View>
);

// ---------------------------------------------------------------- charts built from plain Views
export function SegBar({ parts, height = 12 }: { parts: { value: number; color: string }[]; height?: number }) {
  const total = parts.reduce((a, p) => a + p.value, 0) || 1;
  return (
    <View style={{ flexDirection: 'row', height, borderRadius: height / 2, overflow: 'hidden', backgroundColor: C.greyBg }}>
      {parts.map((p, i) => (p.value > 0 ? <View key={i} style={{ flex: p.value / total, backgroundColor: p.color }} /> : null))}
    </View>
  );
}

// The level scale: three zones, a marker at the student's weighted score.
export function LevelMeter({ score, secure = 0.75, developing = 0.45 }: { score: number | null; secure?: number; developing?: number }) {
  const x = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.timing(x, { toValue: score ?? 0, duration: 900, useNativeDriver: false }).start();
  }, [score, x]);
  const left = x.interpolate({ inputRange: [0, 1], outputRange: ['0%', '100%'] });
  return (
    <View style={{ marginVertical: 10 }}>
      <View style={{ height: 16, borderRadius: 8, flexDirection: 'row', overflow: 'hidden' }}>
        <View style={{ flex: developing, backgroundColor: '#FDBA74' }} />
        <View style={{ flex: secure - developing, backgroundColor: '#93C5FD' }} />
        <View style={{ flex: 1 - secure, backgroundColor: '#86EFAC' }} />
      </View>
      <Animated.View style={{ position: 'absolute', left, top: -4, marginLeft: -10, alignItems: 'center' }}>
        <View style={{ width: 20, height: 24, borderRadius: 10, backgroundColor: C.ink, borderWidth: 3, borderColor: '#fff' }} />
      </Animated.View>
      <View style={{ flexDirection: 'row', marginTop: 6 }}>
        <Text style={{ flex: developing, fontSize: 11, color: C.orange, fontWeight: '700' }}>Basic &lt; {developing}</Text>
        <Text style={{ flex: secure - developing, fontSize: 11, color: C.blue, fontWeight: '700', textAlign: 'center' }}>Medium</Text>
        <Text style={{ flex: 1 - secure, fontSize: 11, color: C.green, fontWeight: '700', textAlign: 'right' }}>Strong ≥ {secure}</Text>
      </View>
    </View>
  );
}

// Donut: segments around a ring with a headline number in the middle.
export function Donut({ segments, size = 110, stroke = 14, center, caption }: { segments: { value: number; color: string }[]; size?: number; stroke?: number; center: string; caption?: string }) {
  const r = (size - stroke) / 2, circ = 2 * Math.PI * r;
  const total = segments.reduce((a, s) => a + s.value, 0);
  let offset = 0;
  return (
    <View style={{ width: size, height: size, alignItems: 'center', justifyContent: 'center' }}>
      <Svg width={size} height={size} style={{ position: 'absolute' }}>
        <Circle cx={size / 2} cy={size / 2} r={r} stroke={C.greyBg} strokeWidth={stroke} fill="none" />
        {total > 0 ? segments.map((s, i) => {
          const len = (s.value / total) * circ;
          const el = s.value > 0 ? (
            <Circle key={i} cx={size / 2} cy={size / 2} r={r} stroke={s.color} strokeWidth={stroke} fill="none"
              strokeDasharray={`${len} ${circ - len}`} strokeDashoffset={-offset} transform={`rotate(-90 ${size / 2} ${size / 2})`} />
          ) : null;
          offset += len;
          return el;
        }) : null}
      </Svg>
      <Text style={{ fontSize: size / 4.2, fontWeight: '800', color: C.ink }}>{center}</Text>
      {caption ? <Text style={{ fontSize: 11, color: C.sub }}>{caption}</Text> : null}
    </View>
  );
}

// Horizontal progress bar that fills in smoothly. value is 0..1.
export function Bar({ value, color = C.teal, label, right, height = 10 }: { value: number; color?: string; label?: string; right?: string; height?: number }) {
  const w = useRef(new Animated.Value(0)).current;
  useEffect(() => { Animated.timing(w, { toValue: Math.max(0, Math.min(1, value)), duration: 700, useNativeDriver: false }).start(); }, [value, w]);
  return (
    <View style={{ marginBottom: 8 }}>
      {label || right ? (
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 }}>
          <Text style={{ fontSize: 13, color: C.ink, fontWeight: '600', flex: 1 }} numberOfLines={1}>{label}</Text>
          <Text style={{ fontSize: 12, color: C.sub }}>{right}</Text>
        </View>
      ) : null}
      <View style={{ height, borderRadius: height / 2, backgroundColor: C.greyBg, overflow: 'hidden' }}>
        <Animated.View style={{ height, borderRadius: height / 2, backgroundColor: color, width: w.interpolate({ inputRange: [0, 1], outputRange: ['0%', '100%'] }) }} />
      </View>
    </View>
  );
}

export function Collapsible({ title, children, open: o = false, icon }: { title: string; children: React.ReactNode; open?: boolean; icon?: string }) {
  const [open, setOpen] = useState(o);
  return (
    <View style={{ marginBottom: 8 }}>
      <Pressable onPress={() => setOpen(!open)} style={{ flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 6 }} accessibilityRole="button">
        {icon ? <Icon name={icon} size={18} color={C.primary} /> : null}
        <Text style={{ flex: 1, fontWeight: '700', color: C.primary, fontSize: 14 }}>{title}</Text>
        <Icon name={open ? 'chevron-up' : 'chevron-down'} size={18} color={C.primary} />
      </Pressable>
      {open ? <View style={{ paddingTop: 4 }}>{children}</View> : null}
    </View>
  );
}

// ---------------------------------------------------------------- states
export const Loading = ({ text = 'Loading…' }: { text?: string }) => (
  <View style={{ padding: 40, alignItems: 'center', gap: 12 }}><ActivityIndicator size="large" color={C.primary} /><Muted>{text}</Muted></View>
);
export const ErrorBox = ({ message, onRetry }: { message: string; onRetry?: () => void }) => (
  <Card accent={C.red}>
    <Row><Icon name="warning" color={C.red} /><T bold style={{ flex: 1 }}>Something went wrong</T></Row>
    <Muted style={{ marginVertical: 8 }}>{message}</Muted>
    {onRetry ? <Btn title="Try again" kind="ghost" onPress={onRetry} /> : null}
  </Card>
);
export const Notice = ({ text, icon = 'information-circle', tone = 'info' }: { text: string; icon?: string; tone?: 'info' | 'warn' }) => (
  <View style={{ flexDirection: 'row', gap: 10, padding: 12, borderRadius: R.s, backgroundColor: tone === 'warn' ? C.amberBg : '#EEF2FF', marginBottom: 12 }}>
    <Icon name={icon} size={18} color={tone === 'warn' ? C.amberText : C.primary} />
    <Text style={{ flex: 1, fontSize: 13, color: tone === 'warn' ? C.amberText : C.primary, lineHeight: 18 }}>{text}</Text>
  </View>
);

export function useLoad<T>(fn: () => Promise<T>, deps: any[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const alive = useRef(true);
  useEffect(() => () => { alive.current = false; }, []);
  const reload = useCallback(() => {
    setLoading(true); setError(null);
    fn().then((d) => { if (alive.current) { setData(d); setLoading(false); } })
      .catch((e) => { if (alive.current) { setError(e.message ?? 'Failed'); setLoading(false); } });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  useEffect(() => { reload(); }, [reload]);
  return { data, error, loading, reload, setData };
}
