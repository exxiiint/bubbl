import http from 'k6/http';
import { check, sleep } from 'k6';

// Демонстрационный x10 read-heavy тест для локальной машины, не доказательство production capacity.
export const options = {
  stages: [
    { duration: '2m', target: 200 },
    { duration: '8m', target: 200 },
    { duration: '2m', target: 0 }
  ],
  thresholds: {
    http_req_failed: ['rate<0.15'],
    http_req_duration: ['p(95)<900']
  }
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const LOGIN = __ENV.LOGIN || 'filipp';
const PASSWORD = __ENV.PASSWORD || 'password123';

function token() {
  const response = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ login: LOGIN, password: PASSWORD }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  return response.json('access_token');
}

export default function () {
  const headers = { Authorization: `Bearer ${token()}` };
  const feed = http.get(`${BASE_URL}/api/feed?limit=30`, { headers });
  check(feed, { 'feed ok': (r) => r.status === 200 });
  const items = feed.json('items') || [];
  if (items.length > 0) {
    const post = items[Math.floor(Math.random() * items.length)];
    http.get(`${BASE_URL}/api/users/${post.author.username}`, { headers });
    http.get(`${BASE_URL}/api/posts/${post.id}`, { headers });
    http.get(`${BASE_URL}/api/posts/${post.id}/comments`, { headers });
  }
  sleep(0.25);
}
