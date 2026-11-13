import { Link } from 'react-router-dom';
import { formatPrice, humanize } from '../../lib/format';
import { toneOf } from '../../lib/statuses';
import { useRemote } from '../../lib/useRemote';
import { getKitchenStats, getMyRestaurant } from '../../services/kitchen';
import Icon from '../../ui/Icon';
import Notice from '../../ui/Notice';
import PageHead from '../../ui/PageHead';
import Spinner from '../../ui/Spinner';
import ReminderPanel from './ReminderPanel';

function Metric({ label, value, foot, to }) {
  const content = (
    <>
      <span className="metric-label">{label}</span>
      <span className="metric-value">{value}</span>
      {foot && <span className="metric-foot">{foot}</span>}
    </>
  );
  return to ? (
    <Link to={to} className="metric is-link">
      {content}
    </Link>
  ) : (
    <div className="metric">{content}</div>
  );
}

function StatusBreakdown({ counts, total }) {
  const rows = Object.entries(counts);
  if (!rows.length) return <p className="subtle">No orders yet.</p>;
  return (
    <ul className="breakdown">
      {rows.map(([status, count]) => (
        <li key={status}>
          <span className="breakdown-label">{humanize(status)}</span>
          <span className="breakdown-track">
            <span
              className={`breakdown-fill tone-${toneOf(status)}`}
              style={{ width: `${total ? (count / total) * 100 : 0}%` }}
            />
          </span>
          <span className="breakdown-count">{count}</span>
        </li>
      ))}
    </ul>
  );
}

export default function KitchenOverview() {
  const restaurant = useRemote(getMyRestaurant, []);
  const stats = useRemote(getKitchenStats, []);

  if (stats.firstLoad) return <Spinner label="Crunching today’s numbers…" />;
  const s = stats.data;

  return (
    <div className="page">
      <PageHead eyebrow="Kitchen overview" title={restaurant.data?.name ?? 'Your kitchen'} lead="How things are going today.">
        <Link to="/kitchen/orders" className="btn btn-primary">
          <Icon name="list" /> Open order queue
        </Link>
        <Link to="/kitchen/menu" className="btn btn-quiet">
          Edit menu
        </Link>
      </PageHead>

      <Notice onRetry={stats.refetch}>{stats.error || restaurant.error}</Notice>

      {s && (
        <div className="metric-row">
          <Metric label="Orders" value={s.total_orders} foot={`${s.orders_today} came in today`} to="/kitchen/orders" />
          <Metric label="Paid revenue" value={formatPrice(s.total_revenue)} foot={`${formatPrice(s.refunded_amount)} refunded`} />
          <Metric
            label="Rating"
            value={s.avg_rating ? s.avg_rating.toFixed(1) : '—'}
            foot={`from ${s.review_count} review${s.review_count === 1 ? '' : 's'}`}
          />
          <Metric label="Refunds to review" value={s.pending_returns} foot="Open the refund desk" to="/kitchen/refunds" />
        </div>
      )}

      <ReminderPanel onChange={stats.refetch} />

      {s && (
        <div className="split split-even">
          <section className="panel">
            <h2 className="panel-title">Where orders stand</h2>
            <StatusBreakdown counts={s.status_counts} total={s.total_orders} />
          </section>
          <section className="panel">
            <h2 className="panel-title">Best sellers</h2>
            {s.top_dishes.length ? (
              <ol className="leaderboard">
                {s.top_dishes.map((dish, index) => (
                  <li key={dish.name}>
                    <span className="rank">{index + 1}</span>
                    <span className="leader-name">{dish.name}</span>
                    <span className="subtle">{dish.quantity} sold</span>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="subtle">Your first sale will show up here.</p>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
