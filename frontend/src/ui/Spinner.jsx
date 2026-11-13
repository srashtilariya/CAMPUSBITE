export default function Spinner({ label = 'Fetching…', inline = false }) {
  return (
    <div className={inline ? 'spinner-inline' : 'spinner-block'} role="status" aria-live="polite">
      <span className="spinner-ring" />
      <span>{label}</span>
    </div>
  );
}
