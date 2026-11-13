import { useState } from 'react';
import { Link } from 'react-router-dom';
import { formatPrice, formatWhen } from '../../lib/format';
import { useAction } from '../../lib/useAction';
import { useRemote } from '../../lib/useRemote';
import { assignCourier, listCouriers, listKitchenOrders, moveOrder } from '../../services/kitchen';
import EmptyState from '../../ui/EmptyState';
import Icon from '../../ui/Icon';
import LineItems from '../../ui/LineItems';
import Notice from '../../ui/Notice';
import PageHead from '../../ui/PageHead';
import Pager from '../../ui/Pager';
import Spinner from '../../ui/Spinner';
import StatusFilterBar from '../../ui/StatusFilterBar';
import StatusPill from '../../ui/StatusPill';

// The forward step a kitchen can take from each status (the API enforces the same rules).
const FORWARD = {
  PLACED: { to: 'ACCEPTED', label: 'Accept' },
  ACCEPTED: { to: 'PREPARING', label: 'Start cooking' },
  PREPARING: { to: 'READY', label: 'Ready for pickup' },
};

function CourierPicker({ couriers, busy, onAssign }) {
  const [choice, setChoice] = useState('');
  return (
    <div className="inline-form">
      <select value={choice} onChange={(e) => setChoice(e.target.value)} aria-label="Rider">
        <option value="">Pick a rider…</option>
        {couriers.map((courier) => (
          <option key={courier.id} value={courier.id}>
            {courier.name}
            {courier.phone ? ` · ${courier.phone}` : ''}
          </option>
        ))}
      </select>
      <button type="button" className="btn btn-primary btn-small" disabled={!choice || busy} onClick={() => onAssign(Number(choice))}>
        <Icon name="bike" size={15} /> Hand over
      </button>
    </div>
  );
}

export default function OrderQueue() {
  const [filters, setFilters] = useState({});
  const [page, setPage] = useState(1);
  const orders = useRemote(() => listKitchenOrders({ ...filters, page, page_size: 8 }), [filters, page]);
  const couriers = useRemote(listCouriers, []);
  const action = useAction(orders.refetch);

  const reject = (order) => {
    if (window.confirm(`Turn down order #${order.id}? The customer will see it as cancelled.`)) {
      action.run(order.id, () => moveOrder(order.id, 'CANCELLED'));
    }
  };

  return (
    <div className="page">
      <PageHead eyebrow="Kitchen" title="Order queue" lead="Move each ticket along as you go.">
        <button type="button" className="btn btn-quiet btn-small" onClick={orders.refetch}>
          <Icon name="refresh" size={16} /> Refresh
        </button>
      </PageHead>

      <StatusFilterBar
        value={filters}
        onChange={(next) => {
          setFilters(next);
          setPage(1);
        }}
      />
      <Notice onRetry={orders.error ? orders.refetch : undefined}>{orders.error || action.error}</Notice>

      {orders.firstLoad ? (
        <Spinner label="Loading tickets…" />
      ) : orders.data?.items.length ? (
        <div className="ticket-list">
          {orders.data.items.map((order) => {
            const step = FORWARD[order.status];
            const busy = action.busyKey === order.id;
            return (
              <article key={order.id} className={`ticket ticket-${order.status.toLowerCase()}`}>
                <header className="ticket-head">
                  <div>
                    <Link to={`/orders/${order.id}`} className="ticket-title">
                      Ticket #{order.id}
                    </Link>
                    <span className="subtle">
                      {formatWhen(order.created_at)} · <Icon name="pin" size={13} /> {order.delivery_address}
                    </span>
                  </div>
                  <StatusPill value={order.status} />
                </header>
                <LineItems items={order.items} compact />
                {order.notes && <p className="callout">“{order.notes}”</p>}
                <footer className="ticket-foot">
                  <div className="ticket-facts">
                    <strong>{formatPrice(order.total_amount)}</strong>
                    <StatusPill value={order.payment_status} prefix="Payment" />
                    {order.return_status !== 'none' && <StatusPill value={order.return_status} prefix="Refund" />}
                  </div>
                  <div className="button-row">
                    {order.status === 'PLACED' && (
                      <button type="button" className="btn btn-danger btn-small" disabled={busy} onClick={() => reject(order)}>
                        Decline
                      </button>
                    )}
                    {step && (
                      <button
                        type="button"
                        className="btn btn-primary btn-small"
                        disabled={busy}
                        onClick={() => action.run(order.id, () => moveOrder(order.id, step.to))}
                      >
                        {step.label}
                      </button>
                    )}
                    {order.status === 'READY' && (
                      <CourierPicker
                        couriers={couriers.data ?? []}
                        busy={busy}
                        onAssign={(partnerId) => action.run(order.id, () => assignCourier(order.id, partnerId))}
                      />
                    )}
                  </div>
                </footer>
              </article>
            );
          })}
        </div>
      ) : (
        !orders.error && (
          <EmptyState icon="list" title="Queue is clear">
            No tickets match the current filters.
          </EmptyState>
        )
      )}

      <Pager result={orders.data} onPage={setPage} />
    </div>
  );
}
