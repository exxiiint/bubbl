import { Link } from 'react-router-dom';
import type { User } from '../../api/client';
import { Avatar } from '../ui/Avatar';
import { GlassPanel } from '../ui/GlassPanel';

export function ProfileMiniCard({ user }: { user: User | null }) {
  if (!user) {
    return null;
  }

  return (
    <GlassPanel as="section" className="profile-mini">
      <div className="profile-mini-head">
        <Avatar src={user.avatar_url} alt={user.display_name} size="lg" />
        <div>
          <h3>Мой профиль</h3>
          <strong>{user.display_name}</strong>
          <span>@{user.username}</span>
        </div>
      </div>
      <div className="mini-stats">
        <div>
          <strong>{user.followers_count}</strong>
          <span>подписчики</span>
        </div>
        <div>
          <strong>{user.following_count}</strong>
          <span>подписки</span>
        </div>
        <div>
          <strong>{user.posts_count}</strong>
          <span>публикации</span>
        </div>
      </div>
      <p className="active-status">активен сегодня</p>
      <Link className="button button-soft button-md full-width" to="/profile/me">
        Редактировать профиль
      </Link>
    </GlassPanel>
  );
}
