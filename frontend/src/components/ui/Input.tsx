import type { InputHTMLAttributes, TextareaHTMLAttributes } from 'react';

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
};

export function Input({ label, className = '', ...props }: InputProps) {
  return (
    <label className="field">
      {label && <span>{label}</span>}
      <input className={`input ${className}`.trim()} {...props} />
    </label>
  );
}

type TextAreaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label?: string;
};

export function TextArea({ label, className = '', ...props }: TextAreaProps) {
  return (
    <label className="field">
      {label && <span>{label}</span>}
      <textarea className={`input textarea ${className}`.trim()} {...props} />
    </label>
  );
}
