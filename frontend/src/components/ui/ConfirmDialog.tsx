import type { ReactNode } from 'react';
import { Button } from './Button';
import { GlassPanel } from './GlassPanel';

type ConfirmDialogProps = {
  open: boolean;
  title: string;
  text: string;
  confirmText?: string;
  cancelText?: string;
  danger?: boolean;
  children?: ReactNode;
  onConfirm: () => void;
  onCancel: () => void;
};

export function ConfirmDialog({
  open,
  title,
  text,
  confirmText = 'Подтвердить',
  cancelText = 'Отмена',
  danger = false,
  children,
  onConfirm,
  onCancel
}: ConfirmDialogProps) {
  if (!open) {
    return null;
  }

  return (
    <div className="modal-backdrop" role="presentation" onClick={onCancel}>
      <GlassPanel className="confirm-dialog" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
        <h3>{title}</h3>
        <p>{text}</p>
        {children}
        <div className="confirm-actions">
          <Button variant="soft" onClick={onCancel}>
            {cancelText}
          </Button>
          <Button variant={danger ? 'danger' : 'primary'} onClick={onConfirm}>
            {confirmText}
          </Button>
        </div>
      </GlassPanel>
    </div>
  );
}
