export default function Notice({ children, tone = 'danger', onRetry }) {
  if (!children) return null;
  return (
    <div className={`notice notice-${tone}`} role={tone === 'danger' ? 'alert' : 'status'}>
      <span>{children}</span>
      {onRetry && (
        <button type="button" className="link-button" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}
