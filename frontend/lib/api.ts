const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token');
}

async function fetchAPI(path: string, options: RequestInit = {}) {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: '요청 실패' }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  if (res.status === 204) return null;
  return res.json();
}

// Auth
export async function register(email: string, password: string, phone?: string) {
  return fetchAPI('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, phone }),
  });
}

export async function login(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString(),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: '로그인 실패' }));
    throw new Error(error.detail);
  }

  const data = await res.json();
  localStorage.setItem('token', data.access_token);
  return data;
}

export async function getMe() {
  return fetchAPI('/auth/me');
}

export function logout() {
  localStorage.removeItem('token');
}

// Conditions
export async function getConditions() {
  return fetchAPI('/conditions');
}

export async function createCondition(data: any) {
  return fetchAPI('/conditions', { method: 'POST', body: JSON.stringify(data) });
}

export async function updateCondition(id: string, data: any) {
  return fetchAPI(`/conditions/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}

export async function deleteCondition(id: string) {
  return fetchAPI(`/conditions/${id}`, { method: 'DELETE' });
}

// Listings
export async function getListings(params?: Record<string, string>) {
  const query = params ? '?' + new URLSearchParams(params).toString() : '';
  return fetchAPI(`/listings${query}`);
}

// Regions
export async function getSido() {
  return fetchAPI('/regions/sido');
}

export async function getSigun(sidoCd: string) {
  return fetchAPI(`/regions/sigun?sido=${sidoCd}`);
}

// Subscription
export async function getSubscription() {
  return fetchAPI('/subscriptions/me');
}

export async function createCheckout(plan: string) {
  return fetchAPI('/subscriptions/checkout', {
    method: 'POST',
    body: JSON.stringify({ plan }),
  });
}
