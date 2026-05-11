import { FormEvent, useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { getErrorMessage } from '../api/client';
import { Button } from '../components/ui/Button';
import { ErrorMessage } from '../components/ui/ErrorMessage';
import { GlassPanel } from '../components/ui/GlassPanel';
import { Input } from '../components/ui/Input';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { useAuth } from '../context/AuthContext';

export function LoginPage() {
  const { login, isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();
  const [loginValue, setLoginValue] = useState('filipp');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (loading) {
    return <LoadingSpinner label="Проверяем сессию" />;
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(loginValue, password);
      navigate('/');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="auth-screen">
      <GlassPanel className="auth-card">
        <div className="auth-logo">bubbl</div>
        <h1>Вход</h1>
        <p>Откройте ленту, профили и уведомления учебной социальной сети.</p>
        <form onSubmit={submit} className="auth-form">
          <Input label="Email или username" value={loginValue} onChange={(event) => setLoginValue(event.target.value)} autoComplete="username" />
          <Input label="Пароль" type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" />
          <ErrorMessage message={error} />
          <Button disabled={busy}>{busy ? 'Входим...' : 'Войти'}</Button>
        </form>
        <span className="auth-link">
          Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
        </span>
      </GlassPanel>
    </main>
  );
}
