import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '5m', target: 20 },
    { duration: '15m', target: 20 },
    { duration: '2m', target: 0 }
  ],
  thresholds: {
    http_req_failed: ['rate<0.10'],
    'http_req_duration{type:feed}': ['p(95)<500'],
    'http_req_duration{type:write}': ['p(95)<300'],
    'http_req_duration{type:login}': ['p(95)<500']
  }
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const LOGIN = __ENV.LOGIN || 'filipp';
const PASSWORD = __ENV.PASSWORD || 'password123';

function authHeaders() {
  const login = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ login: LOGIN, password: PASSWORD }),
    { headers: { 'Content-Type': 'application/json' }, tags: { type: 'login' } }
  );
  check(login, { 'login ok': (r) => r.status === 200 });
  return { Authorization: `Bearer ${login.json('access_token')}`, 'Content-Type': 'application/json' };
}

export default function () {
  const headers = authHeaders();
  const feed = http.get(`${BASE_URL}/api/feed`, { headers, tags: { type: 'feed' } });
  check(feed, { 'feed ok': (r) => r.status === 200 });

  const items = feed.json('items') || [];
  if (items.length > 0) {
    const post = items[Math.floor(Math.random() * items.length)];
    http.get(`${BASE_URL}/api/posts/${post.id}`, { headers, tags: { type: 'feed' } });
    http.post(`${BASE_URL}/api/posts/${post.id}/like`, null, { headers, tags: { type: 'write' } });
    http.post(
      `${BASE_URL}/api/posts/${post.id}/comments`,
      JSON.stringify({ text: `k6 комментарий ${Date.now()}` }),
      { headers, tags: { type: 'write' } }
    );
    http.get(`${BASE_URL}/api/users/${post.author.username}`, { headers, tags: { type: 'feed' } });
  }

  sleep(1);
}
