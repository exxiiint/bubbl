import { useEffect, useState } from 'react';
import { getNotifications } from '../../api/notifications';
import { useAuth } from '../../context/AuthContext';
import { ProfileMiniCard } from '../social/ProfileMiniCard';
import { QuoteWidget } from '../social/QuoteWidget';
import { SearchBar } from '../social/SearchBar';
import { TrendsWidget } from '../social/TrendsWidget';

export function RightRail() {
  const { user } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    getNotifications()
      .then((data) => setUnreadCount(data.unread_count))
      .catch(() => setUnreadCount(0));
  }, []);

  return (
    <aside className="right-rail">
      <SearchBar unreadCount={unreadCount} />
      <TrendsWidget />
      <QuoteWidget />
      <ProfileMiniCard user={user} />
    </aside>
  );
}
