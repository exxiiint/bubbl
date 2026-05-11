import { Share2 } from 'lucide-react';
import { useMemo, useState } from 'react';
import { Button } from '../ui/Button';
import { GlassPanel } from '../ui/GlassPanel';

const quotes = [
  'Будь тем, кто делает мир красивее ✨',
  'Хороший кадр начинается с внимания.',
  'Мягкий свет умеет говорить тише слов.',
  'Красота часто живёт в маленьких деталях.',
  'Публикуй то, что хочется пересмотреть завтра.',
  'Город меняется, если смотреть на него внимательно.',
  'Каждая лента начинается с одного честного кадра.'
];

export function QuoteWidget() {
  const [status, setStatus] = useState<string | null>(null);
  const quote = useMemo(() => {
    const day = Math.floor(Date.now() / 86_400_000);
    return quotes[day % quotes.length];
  }, []);

  const shareQuote = async () => {
    const text = `Цитата дня в bubbl: ${quote}`;
    const showStatus = (message: string) => {
      setStatus(message);
      window.setTimeout(() => setStatus(null), 1800);
    };

    try {
      if (navigator.share) {
        await navigator.share({ title: 'bubbl', text });
        showStatus('Готово');
        return;
      }
    } catch {
      // Пользователь мог закрыть системное окно шаринга, тогда просто пробуем копирование.
    }

    try {
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(text);
        showStatus('Скопировано');
        return;
      }
    } catch {
      // Покажем мягкий статус внутри виджета вместо браузерного alert.
    }

    showStatus('Не удалось поделиться');
  };

  return (
    <GlassPanel as="section" className="widget quote-widget">
      <div className="quote-mark">&ldquo;</div>
      <h3>Цитата дня</h3>
      <p>{quote}</p>
      <Button variant="soft" size="sm" title="Поделиться" onClick={shareQuote}>
        <Share2 size={18} />
        Поделиться
      </Button>
      {status && <span className="quote-status">{status}</span>}
    </GlassPanel>
  );
}
