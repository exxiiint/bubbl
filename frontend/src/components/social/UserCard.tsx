import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { User } from '../../api/client';
import { Avatar } from '../ui/Avatar';
import { GlassPanel } from '../ui/GlassPanel';

export function UserCard({ user }: { user: User }) {
  return (
    <GlassPanel className="user-card">
      <Avatar src={user.avatar_url} alt={user.display_name} />
      <div>
        <strong>{user.display_name}</strong>
        <span>@{user.username}</span>
        {user.bio && <p>{user.bio}</p>}
      </div>
      <Link className="button button-soft button-icon user-card-link" to={`/profile/${user.username}`} aria-label={`Открыть профиль ${user.username}`}>
        <ArrowRight size={18} />
      </Link>
    </GlassPanel>
  );
}
