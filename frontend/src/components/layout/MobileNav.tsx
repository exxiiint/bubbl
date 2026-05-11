import { Bell, Home, PlusSquare, Search, UserRound } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const items = [
  { to: '/', label: 'Главная', icon: Home },
  { to: '/search', label: 'Поиск', icon: Search },
  { to: '/create', label: 'Создать', icon: PlusSquare },
  { to: '/notifications', label: 'Уведомления', icon: Bell },
  { to: '/profile/me', label: 'Профиль', icon: UserRound }
];

export function MobileNav() {
  return (
    <nav className="mobile-nav">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink key={item.to} to={item.to} className={({ isActive }) => (isActive ? 'active' : '')} aria-label={item.label}>
            <Icon size={22} />
          </NavLink>
        );
      })}
    </nav>
  );
}
