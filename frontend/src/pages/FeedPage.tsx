import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getFeed } from '../api/posts';
import type { Post } from '../api/client';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorMessage } from '../components/ui/ErrorMessage';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { PostCard } from '../components/social/PostCard';

export function FeedPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getFeed()
      .then((data) => setPosts(data.items))
      .catch(() => setError('Лента пока не загрузилась'))
      .finally(() => setLoading(false));
  }, []);

  const updatePost = (next: Post) => {
    setPosts((current) => current.map((post) => (post.id === next.id ? next : post)));
  };

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <span>свежие публикации</span>
          <h1>Лента</h1>
        </div>
        <Link className="button button-primary button-md" to="/create">Новая публикация</Link>
      </div>
      {loading && <LoadingSpinner label="Собираем ленту" />}
      <ErrorMessage message={error} />
      {!loading && posts.length === 0 && (
        <EmptyState title="Лента пустая" text="Подпишитесь на пользователей или создайте первую публикацию." />
      )}
      <div className="feed-list">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} onChange={updatePost} onDeleted={(id) => setPosts((current) => current.filter((item) => item.id !== id))} />
        ))}
      </div>
    </section>
  );
}
