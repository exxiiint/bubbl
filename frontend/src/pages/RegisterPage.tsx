import { FormEvent, useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { getErrorMessage } from '../api/client';
import { Button } from '../components/ui/Button';
import { ErrorMessage } from '../components/ui/ErrorMessage';
import { GlassPanel } from '../components/ui/GlassPanel';
import { Input } from '../components/ui/Input';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { useAuth } from '../context/AuthContext';

export function RegisterPage() {
  const { register, isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
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
      await register({ username, display_name: displayName, email, password });
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
        <h1>Регистрация</h1>
        <p>Создайте профиль и загрузите первую публикацию.</p>
        <form onSubmit={submit} className="auth-form">
          <Input label="Username" value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" />
          <Input label="Имя в профиле" value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
          <Input label="Email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" />
          <Input label="Пароль" type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="new-password" />
          <ErrorMessage message={error} />
          <Button disabled={busy}>{busy ? 'Создаём...' : 'Создать аккаунт'}</Button>
        </form>
        <span className="auth-link">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </span>
      </GlassPanel>
    </main>
  );
}
