import type { HTMLAttributes } from 'react';

type GlassPanelProps = HTMLAttributes<HTMLElement> & {
  as?: 'div' | 'section' | 'article' | 'aside' | 'form';
};

export function GlassPanel({ as: Tag = 'div', className = '', children, ...props }: GlassPanelProps) {
  return (
    <Tag className={`glass-panel ${className}`.trim()} {...props}>
      {children}
    </Tag>
  );
}
