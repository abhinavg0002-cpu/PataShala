import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { BackHandler } from 'react-native';

// A tiny stack navigator: fewer packages means fewer Expo Go version problems.
export type Route = { name: string; params?: any };
type Nav = {
  push: (name: string, params?: any) => void;
  pop: () => void;
  replace: (name: string, params?: any) => void;
  reset: (name: string, params?: any) => void;
  canGoBack: boolean;
  route: Route;
};
const NavCtx = createContext<Nav>(null as any);
export const useNav = () => useContext(NavCtx);

export function Navigator({ screens, initial }: { screens: Record<string, React.ComponentType<{ params?: any }>>; initial: Route }) {
  const [stack, setStack] = useState<Route[]>([initial]);
  const push = useCallback((name: string, params?: any) => setStack((s) => [...s, { name, params }]), []);
  const pop = useCallback(() => setStack((s) => (s.length > 1 ? s.slice(0, -1) : s)), []);
  const replace = useCallback((name: string, params?: any) => setStack((s) => [...s.slice(0, -1), { name, params }]), []);
  const reset = useCallback((name: string, params?: any) => setStack([{ name, params }]), []);

  useEffect(() => {
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      if (stack.length > 1) { pop(); return true; }
      return false;
    });
    return () => sub.remove();
  }, [stack.length, pop]);

  const top = stack[stack.length - 1];
  const Screen = screens[top.name];
  return (
    <NavCtx.Provider value={{ push, pop, replace, reset, canGoBack: stack.length > 1, route: top }}>
      <Screen key={stack.length + top.name} params={top.params} />
    </NavCtx.Provider>
  );
}
