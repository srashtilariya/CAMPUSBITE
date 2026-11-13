import { humanize } from '../lib/format';
import { toneOf } from '../lib/statuses';

export default function StatusPill({ value, prefix }) {
  if (!value) return null;
  return (
    <span className={`pill tone-${toneOf(value)}`}>
      <span className="pill-dot" />
      {prefix && <span className="pill-prefix">{prefix}</span>}
      {humanize(value)}
    </span>
  );
}
