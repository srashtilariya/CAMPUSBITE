import { useState } from 'react';
import { requestRefund } from '../../services/orders';
import { describeError } from '../../services/http';
import Dialog from '../../ui/Dialog';
import Notice from '../../ui/Notice';

export default function RefundDialog({ order, onDismiss, onSaved }) {
  const [reason, setReason] = useState('');
  const [saving, setSaving] = useState(false);
  const [problem, setProblem] = useState('');

  const submit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setProblem('');
    try {
      await requestRefund(order.id, reason.trim());
      onSaved?.();
      onDismiss();
    } catch (err) {
      setProblem(describeError(err));
      setSaving(false);
    }
  };

  return (
    <Dialog heading="Ask for a refund" subheading={`Order #${order.id}`} onDismiss={onDismiss}>
      <form className="stack" onSubmit={submit}>
        <Notice>{problem}</Notice>
        <Notice tone="info">
          The kitchen decides on each request. You can only send one per order, so include the details.
        </Notice>
        <label className="field">
          <span>What went wrong?</span>
          <textarea
            rows={4}
            required
            minLength={5}
            maxLength={1000}
            placeholder="Missing item, cold food, wrong order…"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
        </label>
        <button className="btn btn-primary btn-block" disabled={saving}>
          {saving ? 'Sending…' : 'Send request'}
        </button>
      </form>
    </Dialog>
  );
}
