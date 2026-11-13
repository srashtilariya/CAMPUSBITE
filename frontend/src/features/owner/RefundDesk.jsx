import { useState } from 'react';
import { Link } from 'react-router-dom';
import { formatPrice, formatWhen } from '../../lib/format';
import { useAction } from '../../lib/useAction';
import { useRemote } from '../../lib/useRemote';
import { approveRefund, listRefundRequests, rejectRefund } from '../../services/kitchen';
import EmptyState from '../../ui/EmptyState';
import Notice from '../../ui/Notice';
import PageHead from '../../ui/PageHead';
import Pager from '../../ui/Pager';
import Spinner from '../../ui/Spinner';
import StatusPill from '../../ui/StatusPill';

const VIEWS = [
  ['requested', 'Waiting on you'],
  ['approved', 'Approved'],
  ['rejected', 'Declined'],
  ['', 'All'],
];

function DecisionForm({ request, busy, onDecide }) {
  const [note, setNote] = useState('');
  return (
    <div className="decision">
      <input
        placeholder="Message to the customer (optional)"
        value={note}
        onChange={(e) => setNote(e.target.value)}
      />
      <div className="button-row">
        <button type="button" className="btn btn-danger btn-small" disabled={busy} onClick={() => onDecide(request, false, note)}>
          Decline
        </button>
        <button type="button" className="btn btn-primary btn-small" disabled={busy} onClick={() => onDecide(request, true, note)}>
          Approve & refund {formatPrice(request.order_total)}
        </button>
      </div>
    </div>
  );
}

export default function RefundDesk() {
  const [view, setView] = useState('requested');
  const [page, setPage] = useState(1);
  const requests = useRemote(() => listRefundRequests({ status: view, page, page_size: 10 }), [view, page]);
  const action = useAction(requests.refetch);

  const decide = (request, approve, note) => {
    const question = approve
      ? `Refund ${formatPrice(request.order_total)} for order #${request.order_id}?`
      : `Decline the refund for order #${request.order_id}?`;
    if (!window.confirm(question)) return;
    const send = approve ? approveRefund : rejectRefund;
    action.run(request.id, () => send(request.id, note.trim() || null));
  };

  return (
    <div className="page">
      <PageHead eyebrow="Kitchen" title="Refund desk" lead="Read each request and decide. Approved refunds go back automatically." />

      <div className="tabs" role="tablist">
        {VIEWS.map(([value, text]) => (
          <button
            type="button"
            role="tab"
            key={text}
            aria-selected={view === value}
            className={view === value ? 'is-on' : ''}
            onClick={() => {
              setView(value);
              setPage(1);
            }}
          >
            {text}
          </button>
        ))}
      </div>

      <Notice onRetry={requests.error ? requests.refetch : undefined}>{requests.error || action.error}</Notice>

      {requests.firstLoad ? (
        <Spinner label="Loading requests…" />
      ) : requests.data?.items.length ? (
        <div className="ticket-list">
          {requests.data.items.map((request) => (
            <article key={request.id} className="ticket">
              <header className="ticket-head">
                <div>
                  <Link to={`/orders/${request.order_id}`} className="ticket-title">
                    Order #{request.order_id}
                  </Link>
                  <span className="subtle">
                    {request.customer_name} · {formatWhen(request.created_at)} · {formatPrice(request.order_total)}
                  </span>
                </div>
                <StatusPill value={request.status} />
              </header>
              <blockquote className="quote">{request.reason}</blockquote>
              {request.resolution_note && <p className="subtle small">Your reply: {request.resolution_note}</p>}
              {request.status === 'requested' && (
                <DecisionForm request={request} busy={action.busyKey === request.id} onDecide={decide} />
              )}
            </article>
          ))}
        </div>
      ) : (
        !requests.error && (
          <EmptyState icon="undo" title="Nothing in this tray">
            {view === 'requested' ? 'No one is waiting on a refund decision.' : 'No requests to show.'}
          </EmptyState>
        )
      )}

      <Pager result={requests.data} onPage={setPage} />
    </div>
  );
}
