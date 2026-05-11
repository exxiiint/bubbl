import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 1,
  iterations: 1,
  thresholds: {
    http_req_failed: ['rate<0.1'],
    http_req_duration: ['p(95)<700']
  }
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

function login() {
  const response = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ login: __ENV.LOGIN || 'filipp', password: __ENV.PASSWORD || 'password123' }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(response, { 'login 200': (r) => r.status === 200 });
  return response.json('access_token');
}

export default function () {
  const health = http.get(`${BASE_URL}/api/health`);
  check(health, { 'health ok': (r) => r.status === 200 && r.json('status') === 'ok' });

  const token = login();
  const feed = http.get(`${BASE_URL}/api/feed`, { headers: { Authorization: `Bearer ${token}` } });
  check(feed, { 'feed ok': (r) => r.status === 200 });
  sleep(1);
}
