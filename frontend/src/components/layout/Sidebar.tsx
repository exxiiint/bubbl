import { Bell, Home, LogOut, PlusSquare, Search, Settings2, UserRound } from 'lucide-react';
import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Avatar } from '../ui/Avatar';
import { ConfirmDialog } from '../ui/ConfirmDialog';
import { GlassPanel } from '../ui/GlassPanel';

const items = [
  { to: '/', label: 'Главная', icon: Home },
  { to: '/create', label: 'Создать', icon: PlusSquare },
  { to: '/search', label: 'Поиск', icon: Search },
  { to: '/notifications', label: 'Уведомления', icon: Bell },
  { to: '/profile/me', label: 'Профиль', icon: UserRound },
  { to: '/admin', label: 'Админ', icon: Settings2 }
];

export function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [confirmLogout, setConfirmLogout] = useState(false);

  const exit = () => {
    logout();
    setConfirmLogout(false);
    navigate('/login');
  };

  return (
    <GlassPanel as="aside" className="sidebar">
      <NavLink className="brand" to="/">
        bubbl
      </NavLink>
      <nav className="sidebar-nav">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Icon size={20} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
        <button className="nav-item nav-button" onClick={() => setConfirmLogout(true)}>
          <LogOut size={20} />
          <span>Выйти</span>
        </button>
      </nav>
      {user && (
        <div className="sidebar-profile">
          <Avatar src={user.avatar_url} alt={user.display_name} />
          <div>
            <strong>{user.display_name}</strong>
            <span>@{user.username}</span>
          </div>
          <NavLink to="/profile/me">Редактировать профиль</NavLink>
        </div>
      )}
      <ConfirmDialog
        open={confirmLogout}
        title="Выйти из аккаунта?"
        text="Сессия завершится на этом устройстве. Вернуться можно будет через форму входа."
        confirmText="Выйти"
        danger
        onCancel={() => setConfirmLogout(false)}
        onConfirm={exit}
      />
    </GlassPanel>
  );
}
