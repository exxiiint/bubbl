import { UserRound } from 'lucide-react';

type AvatarProps = {
  src?: string | null;
  alt?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
};

export function Avatar({ src, alt = 'Аватар', size = 'md' }: AvatarProps) {
  return (
    <div className={`avatar avatar-${size}`}>
      {src ? <img src={src} alt={alt} /> : <UserRound size={size === 'xl' ? 48 : 24} />}
    </div>
  );
}
