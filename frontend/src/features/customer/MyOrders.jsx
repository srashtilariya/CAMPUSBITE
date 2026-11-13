import { useState } from 'react';
import { Link } from 'react-router-dom';
import { formatPrice, formatWhen } from '../../lib/format';
import { IN_PROGRESS } from '../../lib/statuses';
import { useAction } from '../../lib/useAction';
import { useRemote } from '../../lib/useRemote';
import { cancelOrder, listMyOrders } from '../../services/orders';
import EmptyState from '../../ui/EmptyState';
import Icon from '../../ui/Icon';
import LineItems from '../../ui/LineItems';
import Notice from '../../ui/Notice';
import PageHead from '../../ui/PageHead';
import Pager from '../../ui/Pager';
import Spinner from '../../ui/Spinner';
import StatusFilterBar from '../../ui/StatusFilterBar';
import StatusPill from '../../ui/StatusPill';
import { customerOptions, useOrderDialogs } from './useOrderDialogs';

export default function MyOrders() {
  const [filters, setFilters] = useState({});
  const [page, setPage] = useState(1);

  const orders = useRemote(() => listMyOrders({ ...filters, page, page_size: 8 }), [filters, page]);
  const reload = orders.refetch;
  const action = useAction(reload);
  const dialogs = useOrderDialogs(reload);

  const cancel = (order) => {
    if (window.confirm(`Cancel order #${order.id} from ${order.restaurant_name}?`)) {
      action.run(order.id, () => cancelOrder(order.id));
    }
  };

  const liveCount = orders.data?.items.filter((o) => IN_PROGRESS.includes(o.status)).length ?? 0;

  return (
    <div className="page">
      <PageHead
        eyebrow="History"
        title="My orders"
        lead={liveCount ? `${liveCount} on this page still on the way.` : 'Everything you’ve ordered, newest first.'}
      >
        <Link to="/ask" className="btn btn-quiet">
          <Icon name="sparkle" /> Ask about my orders
        </Link>
      </PageHead>

      <StatusFilterBar
        value={filters}
        onChange={(next) => {
          setFilters(next);
          setPage(1);
        }}
      />

      <Notice onRetry={orders.error ? reload : undefined}>{orders.error || action.error}</Notice>

      {orders.firstLoad ? (
        <Spinner label="Pulling up your orders…" />
      ) : orders.data?.items.length ? (
        <div className="ticket-list">
          {orders.data.items.map((order) => {
            const options = customerOptions(order, order.has_review);
            return (
              <article key={order.id} className="ticket">
                <header className="ticket-head">
                  <div>
                    <Link to={`/orders/${order.id}`} className="ticket-title">
                      {order.restaurant_name}
                    </Link>
                    <span className="subtle">
                      #{order.id} · {formatWhen(order.created_at)}
                    </span>
                  </div>
                  <StatusPill value={order.status} />
                </header>
                <LineItems items={order.items} compact />
                <footer className="ticket-foot">
                  <div className="ticket-facts">
                    <strong>{formatPrice(order.total_amount)}</strong>
                    <StatusPill value={order.payment_status} prefix="Payment" />
                    {order.return_status !== 'none' && <StatusPill value={order.return_status} prefix="Refund" />}
                  </div>
                  <div className="button-row">
                    {options.canCancel && (
                      <button
                        type="button"
                        className="btn btn-danger btn-small"
                        disabled={action.busyKey === order.id}
                        onClick={() => cancel(order)}
                      >
                        Cancel
                      </button>
                    )}
                    {options.canReview && (
                      <button type="button" className="btn btn-primary btn-small" onClick={() => dialogs.openReview(order)}>
                        Rate it
                      </button>
                    )}
                    {options.canRefund && (
                      <button type="button" className="btn btn-quiet btn-small" onClick={() => dialogs.openRefund(order)}>
                        Refund
                      </button>
                    )}
                    <Link to={`/orders/${order.id}`} className="btn btn-quiet btn-small">
                      Details <Icon name="arrowRight" size={14} />
                    </Link>
                  </div>
                </footer>
              </article>
            );
          })}
        </div>
      ) : (
        !orders.error && (
          <EmptyState icon="receipt" title="No orders here">
            <p>Nothing matches yet.</p>
            <Link to="/restaurants" className="btn btn-primary">
              Find something to eat
            </Link>
          </EmptyState>
        )
      )}

      <Pager result={orders.data} onPage={setPage} />
      {dialogs.dialog}
    </div>
  );
}
