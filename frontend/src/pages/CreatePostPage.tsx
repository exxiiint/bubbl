import { ImagePlus, UploadCloud } from 'lucide-react';
import { FormEvent, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createPost } from '../api/posts';
import { getErrorMessage } from '../api/client';
import { Button } from '../components/ui/Button';
import { ErrorMessage } from '../components/ui/ErrorMessage';
import { GlassPanel } from '../components/ui/GlassPanel';
import { TextArea } from '../components/ui/Input';

export function CreatePostPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [caption, setCaption] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) {
      setError('Выберите изображение');
      return;
    }
    const form = new FormData();
    form.append('image', file);
    form.append('caption', caption);
    setBusy(true);
    setError(null);
    try {
      await createPost(form);
      navigate('/');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <span>новая публикация</span>
          <h1>Создать публикацию</h1>
        </div>
      </div>
      <GlassPanel as="form" className="create-card" onSubmit={submit}>
        <label className={`upload-zone ${previewUrl ? 'has-preview' : ''}`}>
          {previewUrl ? (
            <img src={previewUrl} alt="Предпросмотр публикации" />
          ) : (
            <div>
              <UploadCloud size={38} />
              <strong>Выберите изображение</strong>
              <span>Добавьте фото и подпись для ленты.</span>
            </div>
          )}
          <input type="file" accept="image/*" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
        </label>
        <TextArea label="Описание" value={caption} onChange={(event) => setCaption(event.target.value)} rows={5} placeholder="Что происходит на кадре?" />
        <ErrorMessage message={error} />
        <Button disabled={busy}>
          <ImagePlus size={18} />
          {busy ? 'Публикуем...' : 'Опубликовать'}
        </Button>
      </GlassPanel>
    </section>
  );
}
