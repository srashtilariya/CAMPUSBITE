import { formatPrice } from '../lib/format';

export default function LineItems({ items, compact = false }) {
  return (
    <ul className={`line-items ${compact ? 'is-compact' : ''}`}>
      {items.map((item) => (
        <li key={item.id}>
          <span className="line-qty">{item.quantity}×</span>
          <span className="line-name">{item.name}</span>
          <span className="line-amount">{formatPrice(item.unit_price * item.quantity)}</span>
        </li>
      ))}
    </ul>
  );
}
