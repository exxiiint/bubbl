export function LoadingSpinner({ label = 'Загрузка' }: { label?: string }) {
  return (
    <div className="loading">
      <span />
      <p>{label}</p>
    </div>
  );
}
