import { Sparkles } from 'lucide-react';
import { GlassPanel } from './GlassPanel';

export function EmptyState({ title, text }: { title: string; text: string }) {
  return (
    <GlassPanel className="empty-state">
      <Sparkles />
      <h3>{title}</h3>
      <p>{text}</p>
    </GlassPanel>
  );
}
