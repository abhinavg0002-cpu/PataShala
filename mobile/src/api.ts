import AsyncStorage from '@react-native-async-storage/async-storage';
import { DEFAULT_API } from './config';

let base = DEFAULT_API;
let token: string | null = null;

export const getBase = () => base;
export const setBase = (u: string) => { base = u.trim().replace(/\/+$/, ''); };
export const setToken = (t: string | null) => { token = t; };

// Storage can fail (private mode, cleared data): never let that crash the app.
export async function store(key: string, value?: any) {
  try {
    if (value === undefined) {
      const v = await AsyncStorage.getItem(key);
      return v ? JSON.parse(v) : null;
    }
    await AsyncStorage.setItem(key, JSON.stringify(value));
  } catch { /* ignore */ }
  return null;
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) { super(message); this.status = status; }
}

function friendly(detail: any): string {
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length) {
    const f = detail[0];
    const where = Array.isArray(f.loc) ? String(f.loc[f.loc.length - 1]) : '';
    return `Please check "${where}": ${f.msg}`;
  }
  return 'Something went wrong. Please try again.';
}

export async function api<T = any>(path: string, opts: { method?: string; body?: any; params?: Record<string, any> } = {}): Promise<T> {
  let url = base + path;
  if (opts.params) {
    const q = Object.entries(opts.params).map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`).join('&');
    url += (url.includes('?') ? '&' : '?') + q;
  }
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), 15000);
  try {
    const res = await fetch(url, {
      method: opts.method ?? (opts.body ? 'POST' : 'GET'),
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: 'Bearer ' + token } : {}) },
      body: opts.body ? JSON.stringify(opts.body) : undefined,
      signal: ctl.signal,
    });
    const text = await res.text();
    let data: any = null;
    try { data = text ? JSON.parse(text) : null; } catch { /* not JSON */ }
    if (!res.ok) throw new ApiError(friendly(data?.detail), res.status);
    return data as T;
  } catch (e: any) {
    if (e instanceof ApiError) throw e;
    throw new ApiError('Cannot reach the server. Check the Wi-Fi and the server address.', 0);
  } finally {
    clearTimeout(timer);
  }
}

let catalogCache: any = null;
export async function getCatalog() {
  if (!catalogCache) catalogCache = await api('/meta/catalog');
  return catalogCache;
}
