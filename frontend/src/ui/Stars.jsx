import Icon from './Icon';

export function RatingBadge({ rating, count }) {
  if (!rating) return <span className="rating rating-none">New here</span>;
  return (
    <span className="rating">
      <Icon name="star" size={14} className="star-filled" />
      {rating.toFixed(1)}
      {count !== undefined && <span className="subtle">({count})</span>}
    </span>
  );
}

export function StarRow({ value }) {
  return (
    <span className="star-row" aria-label={`${value} out of 5`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <Icon key={n} name="star" size={14} className={n <= value ? 'star-filled' : 'star-empty'} />
      ))}
    </span>
  );
}

export function StarPicker({ value, onChange }) {
  return (
    <div className="star-picker" role="radiogroup" aria-label="Rating">
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          type="button"
          key={n}
          role="radio"
          aria-checked={n === value}
          aria-label={`${n} of 5`}
          className={n <= value ? 'is-lit' : ''}
          onClick={() => onChange(n)}
        >
          <Icon name="star" size={28} />
        </button>
      ))}
    </div>
  );
}
