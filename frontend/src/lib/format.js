const rupees = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const stamp = new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short' });

export const formatPrice = (amount) => rupees.format(Number(amount) || 0);

export const formatWhen = (iso) => (iso ? stamp.format(new Date(iso)) : '—');

/** OUT_FOR_DELIVERY -> "Out for delivery", mock_paid -> "Mock paid" */
export function humanize(code) {
  if (!code) return '';
  const words = String(code).toLowerCase().split('_').join(' ');
  return words.charAt(0).toUpperCase() + words.slice(1);
}

export const plural = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`;

export const firstName = (fullName = '') => fullName.trim().split(/\s+/)[0] || 'there';
