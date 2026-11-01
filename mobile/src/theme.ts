export const C = {
  ink: '#182536',
  sub: '#64748B',
  mute: '#94A3B8',
  bg: '#F6F7F5',
  card: '#FFFFFF',
  line: '#E5E9EC',
  primary: '#142D4E',   // deep navy
  primary2: '#16847F',  // teal
  teal: '#16847F',
  tealBg: '#E4F1F0',
  amber: '#E99A45',     // accent
  orange: '#B45309',
  orangeBg: '#FCF0E1',
  blue: '#2F5D8C',
  blueBg: '#E3ECF5',
  green: '#2E7D4F',
  greenBg: '#E4F2E9',
  grey: '#64748B',
  greyBg: '#E9EDEF',
  red: '#B3372F',
  redBg: '#FBE9E7',
  amberBg: '#FCF0E1',
  amberText: '#8A5A1E',
  violetBg: '#E4F1F0',
};

export const R = { s: 10, m: 14, l: 20 };

// Status is never shown by colour alone: always an icon and a word too.
export const STATUS: Record<string, { label: string; color: string; bg: string; icon: string; short: string }> = {
  needs_support: { label: 'Needs support', color: C.orange, bg: C.orangeBg, icon: 'alert-circle', short: 'N' },
  developing: { label: 'Developing', color: C.blue, bg: C.blueBg, icon: 'trending-up', short: 'D' },
  secure: { label: 'Secure', color: C.green, bg: C.greenBg, icon: 'checkmark-circle', short: 'S' },
  no_evidence: { label: 'Not enough evidence', color: C.grey, bg: C.greyBg, icon: 'ellipse-outline', short: '?' },
};

export const LEVEL: Record<string, { color: string; bg: string; icon: string; blurb: string }> = {
  Basic: { color: C.orange, bg: C.orangeBg, icon: 'construct', blurb: 'Catch-up track: we rebuild the missing basics first.' },
  Medium: { color: C.blue, bg: C.blueBg, icon: 'speedometer', blurb: 'Teacher-led: the teacher guides, the app supports.' },
  Strong: { color: C.green, bg: C.greenBg, icon: 'rocket', blurb: 'Fast track: harder questions, less repeating.' },
};

export const CAUSE: Record<string, { label: string; icon: string; color: string; bg: string; student: string }> = {
  language: { label: 'English / reading load', icon: 'book', color: C.primary2, bg: C.violetBg,
    student: 'The maths or science may be fine. The long words in word problems are making it hard. We will use simpler words.' },
  prerequisite: { label: 'Missing earlier skill', icon: 'git-branch', color: C.orange, bg: C.orangeBg,
    student: 'An earlier skill needs practice first. We will go back and rebuild it.' },
  misconception: { label: 'Misconception', icon: 'bulb', color: C.red, bg: C.redBg,
    student: 'You often pick the same kind of wrong answer. We will show why that idea does not work.' },
  gap: { label: 'Concept gap', icon: 'help-circle', color: C.blue, bg: C.blueBg,
    student: 'This idea needs more practice from the start.' },
  slip: { label: 'Possible slip or guess', icon: 'flash', color: C.amberText, bg: C.amberBg,
    student: 'Looks like a quick slip. Take your time on each one.' },
};

export const DIFF: Record<string, { label: string; color: string; bg: string }> = {
  easy: { label: 'Easy', color: C.green, bg: C.greenBg },
  medium: { label: 'Medium', color: C.blue, bg: C.blueBg },
  hard: { label: 'Hard', color: C.red, bg: C.redBg },
};

export const SUBJECT_ICON: Record<string, string> = { maths: 'calculator', physical: 'flash', biology: 'leaf', telugu: 'language', hindi: 'language', english: 'text', social: 'earth' };
