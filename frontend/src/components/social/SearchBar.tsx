import { Bell, Search } from 'lucide-react';
import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export function SearchBar({ unreadCount = 0 }: { unreadCount?: number }) {
  const navigate = useNavigate();
  const [q, setQ] = useState('');

  const submit = (event: FormEvent) => {
    event.preventDefault();
    navigate(`/search?q=${encodeURIComponent(q)}`);
  };

  return (
    <form className="rail-search" onSubmit={submit}>
      <Search size={18} />
      <input value={q} onChange={(event) => setQ(event.target.value)} placeholder="Поиск..." />
      <button type="button" onClick={() => navigate('/notifications')} title="Уведомления">
        <Bell size={18} />
        {unreadCount > 0 && <span>{unreadCount}</span>}
      </button>
    </form>
  );
}
