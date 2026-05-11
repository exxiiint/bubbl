import { useEffect, useState } from 'react';
import { getTrends } from '../../api/posts';
import type { Trend } from '../../api/client';
import { GlassPanel } from '../ui/GlassPanel';

export function TrendsWidget() {
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTrends()
      .then(setTrends)
      .catch(() => setTrends([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <GlassPanel as="section" className="widget">
      <h3>Тренды</h3>
      <div className="trend-list">
        {loading && <span className="muted-text">Считаем хештеги...</span>}
        {!loading && trends.length === 0 && <span className="muted-text">Хештеги появятся после публикаций.</span>}
        {trends.map((trend) => (
          <div key={trend.tag}>
            <strong>{trend.tag}</strong>
            <span>{trend.posts_count} публикаций</span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}
