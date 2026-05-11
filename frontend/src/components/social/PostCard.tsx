import { Bookmark, Flag, Heart, MessageCircle, MoreHorizontal, Send, Share2, Trash2 } from 'lucide-react';
import { FormEvent, useState } from 'react';
import { Link } from 'react-router-dom';
import { createComment, deletePost, likePost, listComments, unlikePost } from '../../api/posts';
import { createReport } from '../../api/reports';
import type { Comment, Post } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { Avatar } from '../ui/Avatar';
import { Button } from '../ui/Button';
import { ConfirmDialog } from '../ui/ConfirmDialog';
import { ErrorMessage } from '../ui/ErrorMessage';
import { GlassPanel } from '../ui/GlassPanel';
import { TextArea } from '../ui/Input';

type PostCardProps = {
  post: Post;
  onChange?: (post: Post) => void;
  onDeleted?: (postId: string) => void;
};

const dateFormatter = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit'
});

const reportReasons = ['Спам', 'Неуместный контент', 'Оскорбления', 'Нарушение правил', 'Другое'];

export function PostCard({ post, onChange, onDeleted }: PostCardProps) {
  const { user } = useAuth();
  const [commentText, setCommentText] = useState('');
  const [comments, setComments] = useState<Comment[]>([]);
  const [showComments, setShowComments] = useState(false);
  const [busy, setBusy] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [reportOpen, setReportOpen] = useState(false);
  const [reportReason, setReportReason] = useState(reportReasons[0]);
  const [reportDetails, setReportDetails] = useState('');
  const [saved, setSaved] = useState(() => localStorage.getItem(`saved:${post.id}`) === '1');
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const showNotice = (message: string) => {
    setNotice(message);
    window.setTimeout(() => setNotice(null), 1800);
  };

  const toggleLike = async () => {
    setBusy(true);
    setError(null);
    try {
      const next = post.liked_by_me ? await unlikePost(post.id) : await likePost(post.id);
      onChange?.(next);
    } catch {
      setError('Не удалось обновить лайк');
    } finally {
      setBusy(false);
    }
  };

  const loadComments = async () => {
    setError(null);
    try {
      const data = await listComments(post.id);
      setComments(data);
      setShowComments(true);
    } catch {
      setError('Не удалось загрузить комментарии');
    }
  };

  const submitComment = async (event: FormEvent) => {
    event.preventDefault();
    const text = commentText.trim();
    if (!text) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const comment = await createComment(post.id, text);
      setComments((current) => [...current, comment]);
      setCommentText('');
      onChange?.({ ...post, comments_count: post.comments_count + 1 });
    } catch {
      setError('Комментарий не отправился');
    } finally {
      setBusy(false);
    }
  };

  const removePost = async () => {
    setBusy(true);
    setError(null);
    try {
      await deletePost(post.id);
      onDeleted?.(post.id);
    } catch {
      setError('Не удалось удалить публикацию');
    } finally {
      setBusy(false);
      setConfirmDelete(false);
    }
  };

  const sharePost = async () => {
    const url = `${window.location.origin}/profile/${post.author.username}`;
    const text = `Публикация ${post.author.display_name} в bubbl`;
    try {
      if (navigator.share) {
        await navigator.share({ title: 'bubbl', text, url });
      } else {
        await navigator.clipboard.writeText(url);
        showNotice('Ссылка скопирована');
      }
    } catch {
      await navigator.clipboard.writeText(url);
      showNotice('Ссылка скопирована');
    }
  };

  const toggleSaved = () => {
    const next = !saved;
    setSaved(next);
    localStorage.setItem(`saved:${post.id}`, next ? '1' : '0');
    showNotice(next ? 'Публикация сохранена' : 'Публикация убрана из сохранённых');
  };

  const submitReport = async () => {
    setBusy(true);
    setError(null);
    try {
      await createReport(post.id, reportReason, reportDetails);
      setReportOpen(false);
      setReportDetails('');
      setMenuOpen(false);
      showNotice('Жалоба отправлена');
    } catch {
      setError('Не удалось отправить жалобу');
    } finally {
      setBusy(false);
    }
  };

  return (
    <GlassPanel as="article" className="post-card">
      <header className="post-header">
        <Link className="post-author" to={`/profile/${post.author.username}`}>
          <Avatar src={post.author.avatar_url} alt={post.author.display_name} />
          <div>
            <strong>{post.author.display_name}</strong>
            <span>@{post.author.username} · {dateFormatter.format(new Date(post.created_at))}</span>
          </div>
        </Link>
        <div className="post-header-actions">
          {user?.id === post.author.id && (
            <Button variant="ghost" size="icon" title="Удалить публикацию" onClick={() => setConfirmDelete(true)} disabled={busy}>
              <Trash2 size={18} />
            </Button>
          )}
          <div className="post-more">
            <Button variant="ghost" size="icon" title="Ещё" onClick={() => setMenuOpen((value) => !value)}>
              <MoreHorizontal size={20} />
            </Button>
            {menuOpen && (
              <div className="post-menu">
                <button type="button" onClick={() => setReportOpen(true)}>
                  <Flag size={16} />
                  Пожаловаться
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <img className="post-image" src={post.media_url} alt={post.caption || 'Публикация bubbl'} />

      <div className="post-actions">
        <Button variant={post.liked_by_me ? 'primary' : 'soft'} size="icon" title="Лайк" onClick={toggleLike} disabled={busy}>
          <Heart size={20} fill={post.liked_by_me ? 'currentColor' : 'none'} />
        </Button>
        <Button variant="soft" size="icon" title="Комментарии" onClick={showComments ? undefined : loadComments}>
          <MessageCircle size={20} />
        </Button>
        <Button variant="soft" size="icon" title="Поделиться" onClick={sharePost}>
          <Share2 size={20} />
        </Button>
        <Button variant={saved ? 'primary' : 'soft'} size="icon" title="Сохранить" onClick={toggleSaved}>
          <Bookmark size={20} fill={saved ? 'currentColor' : 'none'} />
        </Button>
      </div>

      <div className="post-copy">
        <strong>{post.likes_count} лайков</strong>
        {post.caption && (
          <p>
            <Link to={`/profile/${post.author.username}`}>@{post.author.username}</Link> {post.caption}
          </p>
        )}
        {!showComments && post.comments_count > 0 && (
          <button className="text-button" onClick={loadComments}>
            Смотреть все комментарии ({post.comments_count})
          </button>
        )}
      </div>

      {showComments && (
        <div className="comments-list">
          {comments.map((comment) => (
            <p key={comment.id}>
              <Link to={`/profile/${comment.user.username}`}>@{comment.user.username}</Link> {comment.text}
            </p>
          ))}
        </div>
      )}

      <form className="comment-form" onSubmit={submitComment}>
        <input value={commentText} onChange={(event) => setCommentText(event.target.value)} placeholder="Добавить комментарий..." />
        <Button size="icon" title="Отправить" disabled={busy || !commentText.trim()}>
          <Send size={18} />
        </Button>
      </form>
      {notice && <div className="inline-notice">{notice}</div>}
      <ErrorMessage message={error} />

      <ConfirmDialog
        open={confirmDelete}
        title="Удалить публикацию?"
        text="Публикация исчезнет из ленты и профиля. Это действие нельзя будет отменить."
        confirmText="Удалить"
        danger
        onCancel={() => setConfirmDelete(false)}
        onConfirm={removePost}
      />

      <ConfirmDialog
        open={reportOpen}
        title="Пожаловаться на публикацию"
        text="Админ увидит жалобу, автора публикации и причину."
        confirmText="Отправить жалобу"
        onCancel={() => setReportOpen(false)}
        onConfirm={submitReport}
      >
        <label className="field">
          <span>Причина</span>
          <select className="input" value={reportReason} onChange={(event) => setReportReason(event.target.value)}>
            {reportReasons.map((reason) => (
              <option key={reason} value={reason}>
                {reason}
              </option>
            ))}
          </select>
        </label>
        <TextArea
          label="Комментарий"
          rows={3}
          value={reportDetails}
          onChange={(event) => setReportDetails(event.target.value)}
          placeholder="Можно добавить детали"
        />
      </ConfirmDialog>
    </GlassPanel>
  );
}
