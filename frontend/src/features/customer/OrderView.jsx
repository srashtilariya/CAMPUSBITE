import { Link, useLocation, useParams } from 'react-router-dom';
import { formatPrice, formatWhen, humanize } from '../../lib/format';
import { useAction } from '../../lib/useAction';
import { useRemote } from '../../lib/useRemote';
import { cancelOrder, getOrder } from '../../services/orders';
import { useSession } from '../../state/SessionProvider';
import Icon from '../../ui/Icon';
import LineItems from '../../ui/LineItems';
import Notice from '../../ui/Notice';
import OrderTimeline from '../../ui/OrderTimeline';
import Spinner from '../../ui/Spinner';
import { StarRow } from '../../ui/Stars';
import StatusPill from '../../ui/StatusPill';
import { customerOptions, useOrderDialogs } from './useOrderDialogs';

const RETURN_PATH = {
  customer: ['/orders', 'My orders'],
  restaurant_owner: ['/kitchen/orders', 'Order queue'],
  delivery_partner: ['/rides', 'Active drops'],
};

function PaymentLedger({ entries }) {
  if (!entries?.length) return <p className="subtle">No payment entries yet.</p>;
  return (
    <table className="ledger">
      <tbody>
        {entries.map((entry) => {
          const isRefund = entry.entry_type === 'refund';
          return (
            <tr key={entry.id} className={isRefund ? 'is-refund' : ''}>
              <td>
                <strong>{humanize(entry.entry_type)}</strong>
                <small className="subtle">{entry.reference}</small>
              </td>
              <td className="num">
                {isRefund ? '−' : '+'}
                {formatPrice(entry.amount)}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export default function OrderView() {
  const { orderId } = useParams();
  const { user } = useSession();
  const { state } = useLocation();
  const { data: order, firstLoad, error, refetch, loading } = useRemote(() => getOrder(orderId), [orderId]);
  const action = useAction(refetch);
  const dialogs = useOrderDialogs(refetch);

  if (firstLoad) return <Spinner label="Looking up this order…" />;
  if (error && !order) {
    return (
      <div className="page page-narrow">
        <Notice onRetry={refetch}>{error}</Notice>
      </div>
    );
  }

  const [backTo, backLabel] = RETURN_PATH[user.role] ?? ['/', 'Home'];
  const options = customerOptions(order, Boolean(order.review));
  const isCustomer = user.role === 'customer';
  const refund = order.return_request;

  const cancel = () => {
    if (window.confirm('Cancel this order? The kitchen hasn’t started on it yet.')) {
      action.run('cancel', () => cancelOrder(order.id));
    }
  };

  return (
    <div className="page page-narrow">
      <Link to={backTo} className="back">
        <Icon name="arrowLeft" size={16} /> {backLabel}
      </Link>

      {state?.fresh && (
        <Notice tone="success">Order confirmed and paid (simulated). The kitchen has been notified.</Notice>
      )}

      <header className="page-head">
        <div>
          <span className="eyebrow">Order #{order.id}</span>
          <h1>{order.restaurant_name}</h1>
          <p className="lead">Placed {formatWhen(order.created_at)}</p>
        </div>
        <div className="page-head-actions">
          <button type="button" className="btn btn-quiet btn-small" onClick={refetch} disabled={loading}>
            <Icon name="refresh" size={16} /> {loading ? 'Updating…' : 'Update'}
          </button>
        </div>
      </header>

      <Notice>{action.error}</Notice>

      <section className="panel">
        <OrderTimeline status={order.status} />
        <p className="subtle small">Last change {formatWhen(order.updated_at)}</p>
      </section>

      <div className="split split-even">
        <section className="panel">
          <h2 className="panel-title">What you ordered</h2>
          <LineItems items={order.items} />
          <div className="sum-row">
            <span>Total</span>
            <strong>{formatPrice(order.total_amount)}</strong>
          </div>
          {order.notes && (
            <p className="callout">
              <strong>Kitchen note:</strong> {order.notes}
            </p>
          )}
        </section>

        <div className="stack">
          <section className="panel">
            <h2 className="panel-title">Delivery</h2>
            <p className="icon-line">
              <Icon name="pin" size={16} /> {order.delivery_address}
            </p>
            {order.delivery_partner ? (
              <p className="icon-line">
                <Icon name="bike" size={16} /> {order.delivery_partner.name}
                {order.delivery_partner.phone && (
                  <a href={`tel:${order.delivery_partner.phone}`}> · {order.delivery_partner.phone}</a>
                )}
              </p>
            ) : (
              <p className="subtle">A rider will be assigned once the food is ready.</p>
            )}
          </section>

          <section className="panel">
            <div className="panel-title-row">
              <h2 className="panel-title">Payments</h2>
              <StatusPill value={order.payment_status} />
            </div>
            <PaymentLedger entries={order.payments} />
          </section>

          {refund && (
            <section className="panel">
              <div className="panel-title-row">
                <h2 className="panel-title">Refund request</h2>
                <StatusPill value={refund.status} />
              </div>
              <p className="small">“{refund.reason}”</p>
              {refund.resolution_note && (
                <p className="callout">
                  <strong>Kitchen replied:</strong> {refund.resolution_note}
                </p>
              )}
            </section>
          )}

          {order.review && (
            <section className="panel">
              <h2 className="panel-title">Your rating</h2>
              <StarRow value={order.review.rating} />
              {order.review.comment && <p className="small">{order.review.comment}</p>}
            </section>
          )}
        </div>
      </div>

      {isCustomer && (options.canCancel || options.canReview || options.canRefund) && (
        <div className="button-row action-bar">
          {options.canCancel && (
            <button type="button" className="btn btn-danger" disabled={action.busyKey === 'cancel'} onClick={cancel}>
              Cancel order
            </button>
          )}
          {options.canReview && (
            <button type="button" className="btn btn-primary" onClick={() => dialogs.openReview(order)}>
              Rate this order
            </button>
          )}
          {options.canRefund && (
            <button type="button" className="btn btn-quiet" onClick={() => dialogs.openRefund(order)}>
              Something wrong? Ask for a refund
            </button>
          )}
        </div>
      )}
      {dialogs.dialog}
    </div>
  );
}
