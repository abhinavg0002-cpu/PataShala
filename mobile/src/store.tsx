import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { setToken, store } from './api';

export type User = {
  id: number; code: string; role: 'student' | 'teacher'; name: string; school: string; branch: string;
  roll_no?: string; class_no?: number; section?: string; board?: string; state?: string; gender?: string;
  area_type?: string; locality?: string; demo_persona?: string | null;
};
type Known = { code: string; name: string; role: string };

type Ctx = {
  user: User | null;
  known: Known[];
  signIn: (resp: { token: string; user: User }) => void;
  signOut: () => void;
  forget: (code: string) => void;
};
const AuthCtx = createContext<Ctx>(null as any);
export const useAuth = () => useContext(AuthCtx);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [known, setKnown] = useState<Known[]>([]);

  useEffect(() => { store('known_users').then((k) => k && setKnown(k)); }, []);

  const signIn = useCallback((resp: { token: string; user: User }) => {
    setToken(resp.token);
    setUser(resp.user);
    // Shared-device list: names and ID codes only. PINs and tokens are never saved.
    setKnown((prev) => {
      const next = [{ code: resp.user.code, name: resp.user.name, role: resp.user.role }, ...prev.filter((k) => k.code !== resp.user.code)].slice(0, 8);
      store('known_users', next);
      return next;
    });
  }, []);
  const signOut = useCallback(() => { setToken(null); setUser(null); }, []);
  const forget = useCallback((code: string) => {
    setKnown((prev) => { const next = prev.filter((k) => k.code !== code); store('known_users', next); return next; });
  }, []);

  return <AuthCtx.Provider value={{ user, known, signIn, signOut, forget }}>{children}</AuthCtx.Provider>;
}
