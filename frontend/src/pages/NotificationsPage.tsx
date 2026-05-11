import { CheckCheck } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getNotifications, readAllNotifications } from '../api/notifications';
import type { NotificationItem } from '../api/client';
import { Avatar } from '../components/ui/Avatar';
import { Button } from '../components/ui/Button';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorMessage } from '../components/ui/ErrorMessage';
import { GlassPanel } from '../components/ui/GlassPanel';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

const formatter = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit'
});

export function NotificationsPage() {
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getNotifications()
      .then((data) => {
        setItems(data.items);
        setUnreadCount(data.unread_count);
      })
      .catch(() => setError('Уведомления не загрузились'))
      .finally(() => setLoading(false));
  }, []);

  const markRead = async () => {
    setBusy(true);
    setError(null);
    try {
      const data = await readAllNotifications();
      setItems(data.items);
      setUnreadCount(data.unread_count);
    } catch {
      setError('Не удалось отметить уведомления');
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <span>{unreadCount} непрочитанных</span>
          <h1>Уведомления</h1>
        </div>
        <Button variant="soft" onClick={markRead} disabled={busy || unreadCount === 0}>
          <CheckCheck size={18} />
          Отметить все прочитанными
        </Button>
      </div>
      {loading && <LoadingSpinner label="Проверяем события" />}
      <ErrorMessage message={error} />
      {!loading && items.length === 0 && <EmptyState title="Пока тихо" text="Лайки, комментарии и подписки появятся здесь." />}
      <GlassPanel className="notifications-list">
        {items.map((item) => (
          <Link
            key={item.id}
            to={item.actor ? `/profile/${item.actor.username}` : '/notifications'}
            className={`notification-row ${item.is_read ? '' : 'unread'}`}
          >
            <Avatar src={item.actor?.avatar_url} alt={item.actor?.display_name ?? 'Событие'} />
            <div>
              <strong>{item.actor?.display_name ?? 'Система'}</strong>
              <p>{item.text}</p>
            </div>
            <span>{formatter.format(new Date(item.created_at))}</span>
          </Link>
        ))}
      </GlassPanel>
    </section>
  );
}
