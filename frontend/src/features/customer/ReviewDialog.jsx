import { useState } from 'react';
import { reviewOrder } from '../../services/orders';
import { describeError } from '../../services/http';
import Dialog from '../../ui/Dialog';
import Notice from '../../ui/Notice';
import { StarPicker } from '../../ui/Stars';

const MOODS = ['', 'Not great', 'Could be better', 'It was okay', 'Really good', 'Loved it'];

export default function ReviewDialog({ order, onDismiss, onSaved }) {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [saving, setSaving] = useState(false);
  const [problem, setProblem] = useState('');

  const submit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setProblem('');
    try {
      await reviewOrder(order.id, { rating, comment: comment.trim() || null });
      onSaved?.();
      onDismiss();
    } catch (err) {
      setProblem(describeError(err));
      setSaving(false);
    }
  };

  return (
    <Dialog heading="How was it?" subheading={`Order #${order.id} · ${order.restaurant_name}`} onDismiss={onDismiss}>
      <form className="stack" onSubmit={submit}>
        <Notice>{problem}</Notice>
        <div className="rating-input">
          <StarPicker value={rating} onChange={setRating} />
          <span className="subtle">{MOODS[rating]}</span>
        </div>
        <label className="field">
          <span>Anything to add? <em>(optional)</em></span>
          <textarea
            rows={3}
            maxLength={1000}
            placeholder="Tell other students what stood out"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
        </label>
        <button className="btn btn-primary btn-block" disabled={saving}>
          {saving ? 'Posting…' : 'Post review'}
        </button>
      </form>
    </Dialog>
  );
}
