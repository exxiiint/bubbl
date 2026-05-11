import { Camera, Edit3, HeartHandshake, Image as ImageIcon, UserMinus, UserPlus } from 'lucide-react';
import { FormEvent, useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getErrorMessage, type Post, type User } from '../api/client';
import { followUser, getMe, getUser, getUserPosts, unfollowUser, updateMe } from '../api/users';
import { Avatar } from '../components/ui/Avatar';
import { Button } from '../components/ui/Button';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorMessage } from '../components/ui/ErrorMessage';
import { GlassPanel } from '../components/ui/GlassPanel';
import { Input, TextArea } from '../components/ui/Input';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { StatCard } from '../components/ui/StatCard';
import { useAuth } from '../context/AuthContext';

type ProfilePageProps = {
  mode: 'me' | 'user';
};

export function ProfilePage({ mode }: ProfilePageProps) {
  const params = useParams();
  const { user: currentUser, setUser } = useAuth();
  const [profile, setProfile] = useState<User | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [displayName, setDisplayName] = useState('');
  const [bio, setBio] = useState('');
  const [avatar, setAvatar] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isMe = mode === 'me' || profile?.id === currentUser?.id;
  const previewUrl = useMemo(() => (avatar ? URL.createObjectURL(avatar) : profile?.avatar_url ?? null), [avatar, profile?.avatar_url]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = mode === 'me' ? await getMe() : await getUser(params.username ?? '');
        setProfile(data);
        setDisplayName(data.display_name);
        setBio(data.bio ?? '');
        const userPosts = await getUserPosts(data.id);
        setPosts(userPosts);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [mode, params.username]);

  const submitProfile = async (event: FormEvent) => {
    event.preventDefault();
    const form = new FormData();
    form.append('display_name', displayName);
    form.append('bio', bio);
    if (avatar) {
      form.append('avatar', avatar);
    }
    setBusy(true);
    setError(null);
    try {
      const updated = await updateMe(form);
      setProfile(updated);
      setUser(updated);
      setEditing(false);
      setAvatar(null);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const toggleFollow = async () => {
    if (!profile) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const updated = profile.is_following ? await unfollowUser(profile.id) : await followUser(profile.id);
      setProfile(updated);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  if (loading) {
    return <LoadingSpinner label="Открываем профиль" />;
  }

  if (!profile) {
    return <ErrorMessage message={error ?? 'Профиль не найден'} />;
  }

  return (
    <section className="page-stack">
      <GlassPanel as="section" className="profile-header">
        <div className="profile-top">
          <Avatar src={previewUrl} alt={profile.display_name} size="xl" />
          <div className="profile-title">
            <span>@{profile.username}</span>
            <h1>{profile.display_name}</h1>
            <p>{profile.bio || 'Пользователь пока не добавил описание.'}</p>
          </div>
          {isMe ? (
            <Button variant="soft" onClick={() => setEditing((value) => !value)}>
              <Edit3 size={18} />
              Редактировать профиль
            </Button>
          ) : (
            <Button onClick={toggleFollow} disabled={busy}>
              {profile.is_following ? <UserMinus size={18} /> : <UserPlus size={18} />}
              {profile.is_following ? 'Отписаться' : 'Подписаться'}
            </Button>
          )}
        </div>
        <div className="profile-stats">
          <StatCard label="публикации" value={profile.posts_count} icon={<ImageIcon size={18} />} />
          <StatCard label="подписчики" value={profile.followers_count} icon={<HeartHandshake size={18} />} />
          <StatCard label="подписки" value={profile.following_count} icon={<UserPlus size={18} />} />
        </div>
        {editing && (
          <form className="edit-profile-form" onSubmit={submitProfile}>
            <Input label="Имя" value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
            <TextArea label="О себе" rows={3} value={bio} onChange={(event) => setBio(event.target.value)} />
            <label className="avatar-upload">
              <Camera size={18} />
              <span>{avatar ? avatar.name : 'Новый аватар'}</span>
              <input type="file" accept="image/*" onChange={(event) => setAvatar(event.target.files?.[0] ?? null)} />
            </label>
            <Button disabled={busy}>{busy ? 'Сохраняем...' : 'Сохранить'}</Button>
          </form>
        )}
        <ErrorMessage message={error} />
      </GlassPanel>

      {posts.length === 0 ? (
        <EmptyState title="Публикаций пока нет" text={isMe ? 'Создайте первую публикацию.' : 'Здесь скоро появятся изображения.'} />
      ) : (
        <div className="posts-grid">
          {posts.map((post) => (
            <Link key={post.id} to={`/profile/${profile.username}`} className="grid-post">
              <img src={post.media_url} alt={post.caption || 'Публикация'} />
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
