import { Activity, ArrowLeft, Database, FileText, Flag, Heart, MessageCircle, Server, Users } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getReports, markReportReviewed } from '../api/reports';
import { externalLinks, getHealth, getStats } from '../api/system';
import type { Report, SystemStats } from '../api/client';
import { Avatar } from '../components/ui/Avatar';
import { Button } from '../components/ui/Button';
import { ErrorMessage } from '../components/ui/ErrorMessage';
import { GlassPanel } from '../components/ui/GlassPanel';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { StatCard } from '../components/ui/StatCard';

export function SystemPage() {
  const [health, setHealth] = useState<string>('unknown');
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [reportsLoading, setReportsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getHealth(), getStats()])
      .then(([healthData, statsData]) => {
        setHealth(healthData.status);
        setStats(statsData);
      })
      .catch(() => setError('Системные данные не загрузились'))
      .finally(() => setLoading(false));

    getReports('open')
      .then(setReports)
      .catch(() => setReportError('Жалобы не загрузились'))
      .finally(() => setReportsLoading(false));
  }, []);

  const reviewReport = async (reportId: string) => {
    setReportError(null);
    try {
      await markReportReviewed(reportId);
      setReports((current) => current.filter((report) => report.id !== reportId));
      setStats((current) => (current ? { ...current, reports_count: Math.max(0, current.reports_count - 1) } : current));
    } catch {
      setReportError('Не удалось обработать жалобу');
    }
  };

  return (
    <main className="admin-screen">
      <section className="admin-shell">
        <div className="admin-topbar">
          <Link className="button button-soft button-md" to="/">
            <ArrowLeft size={18} />
            В приложение
          </Link>
          <strong>bubbl admin</strong>
        </div>
        <div className="page-stack">
          <div className="page-heading">
            <div>
              <span>служебная зона</span>
              <h1>Админ-панель</h1>
            </div>
          </div>
          {loading && <LoadingSpinner label="Опрашиваем backend" />}
          <ErrorMessage message={error} />
          <GlassPanel className="system-health">
            <Activity />
            <div>
              <span>Состояние сервиса</span>
              <strong>{health}</strong>
            </div>
          </GlassPanel>
          {stats && (
            <div className="system-grid">
              <StatCard label="пользователей" value={stats.users_count} icon={<Users size={18} />} />
              <StatCard label="публикаций" value={stats.posts_count} icon={<FileText size={18} />} />
              <StatCard label="лайков" value={stats.likes_count} icon={<Heart size={18} />} />
              <StatCard label="комментариев" value={stats.comments_count} icon={<MessageCircle size={18} />} />
              <StatCard label="жалоб" value={stats.reports_count} icon={<Flag size={18} />} />
            </div>
          )}
          <GlassPanel className="admin-reports">
            <div className="admin-section-head">
              <div>
                <span>модерация</span>
                <h2>Жалобы</h2>
              </div>
              <strong>{reports.length} открытых</strong>
            </div>
            {reportsLoading && <LoadingSpinner label="Загружаем жалобы" />}
            <ErrorMessage message={reportError} />
            {!reportsLoading && reports.length === 0 && <p className="muted-text">Открытых жалоб нет.</p>}
            <div className="report-list">
              {reports.map((report) => (
                <article className="report-row" key={report.id}>
                  {report.post_media_url ? (
                    <img src={report.post_media_url} alt="Публикация с жалобой" />
                  ) : (
                    <div className="report-placeholder">
                      <Flag size={20} />
                    </div>
                  )}
                  <div>
                    <div className="report-title">
                      <strong>{report.reason}</strong>
                      <span>{new Date(report.created_at).toLocaleString('ru-RU')}</span>
                    </div>
                    <p>{report.post_caption || 'Публикация без описания'}</p>
                    {report.details && <p className="muted-text">{report.details}</p>}
                    <Link className="reporter-link" to={`/profile/${report.reporter.username}`}>
                      <Avatar src={report.reporter.avatar_url} alt={report.reporter.display_name} size="sm" />
                      @{report.reporter.username}
                    </Link>
                  </div>
                  <Button variant="soft" onClick={() => reviewReport(report.id)}>
                    Обработано
                  </Button>
                </article>
              ))}
            </div>
          </GlassPanel>
          <GlassPanel className="system-links">
            <a href={externalLinks.swagger} target="_blank" rel="noreferrer">
              <Server size={18} />
              Swagger
            </a>
            <a href={externalLinks.minio} target="_blank" rel="noreferrer">
              <Database size={18} />
              MinIO Console
            </a>
            <a href={externalLinks.health} target="_blank" rel="noreferrer">
              <Activity size={18} />
              Проверка здоровья
            </a>
          </GlassPanel>
        </div>
      </section>
    </main>
  );
}
