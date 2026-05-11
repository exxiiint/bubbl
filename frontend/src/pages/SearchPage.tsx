import { Search } from 'lucide-react';
import { FormEvent, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { searchUsers } from '../api/users';
import type { User } from '../api/client';
import { UserCard } from '../components/social/UserCard';
import { Button } from '../components/ui/Button';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorMessage } from '../components/ui/ErrorMessage';
import { GlassPanel } from '../components/ui/GlassPanel';
import { Input } from '../components/ui/Input';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

export function SearchPage() {
  const [params, setParams] = useSearchParams();
  const initial = params.get('q') ?? '';
  const [query, setQuery] = useState(initial);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(Boolean(initial));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const q = params.get('q') ?? '';
    setQuery(q);
    if (!q) {
      setUsers([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    searchUsers(q)
      .then(setUsers)
      .catch(() => setError('Поиск не сработал'))
      .finally(() => setLoading(false));
  }, [params]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    setParams(query ? { q: query } : {});
  };

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <span>найдите людей в bubbl</span>
          <h1>Поиск</h1>
        </div>
      </div>
      <GlassPanel as="form" className="search-page-form" onSubmit={submit}>
        <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Например, anya" />
        <Button size="icon" title="Искать">
          <Search size={18} />
        </Button>
      </GlassPanel>
      {loading && <LoadingSpinner label="Ищем пользователей" />}
      <ErrorMessage message={error} />
      {!loading && query && users.length === 0 && <EmptyState title="Ничего не найдено" text="Попробуйте другой username или имя." />}
      <div className="users-list">
        {users.map((user) => (
          <UserCard key={user.id} user={user} />
        ))}
      </div>
    </section>
  );
}
