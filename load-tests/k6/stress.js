import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '5m', target: 30 },
    { duration: '10s', target: 40 },
    { duration: '10s', target: 50 },
    { duration: '10s', target: 70 },
    { duration: '10s', target: 90 },
    { duration: '2m', target: 0 }
  ],
  thresholds: {
    http_req_failed: ['rate<0.25']
  }
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const LOGIN = __ENV.LOGIN || 'filipp';
const PASSWORD = __ENV.PASSWORD || 'password123';

function getToken() {
  const response = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ login: LOGIN, password: PASSWORD }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(response, { 'login ok': (r) => r.status === 200 });
  return response.json('access_token');
}

export default function () {
  const token = getToken();
  const headers = { Authorization: `Bearer ${token}` };
  const feed = http.get(`${BASE_URL}/api/feed?limit=20`, { headers });
  check(feed, { 'feed ok': (r) => r.status === 200 });
  sleep(0.5);
}
