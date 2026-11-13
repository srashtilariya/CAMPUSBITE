import { useState } from 'react';
import { formatPrice, formatWhen } from '../../lib/format';
import { COURIER_STATUSES } from '../../lib/statuses';
import { useAction } from '../../lib/useAction';
import { useRemote } from '../../lib/useRemote';
import { listAssignedDrops, updateDropStatus } from '../../services/courier';
import EmptyState from '../../ui/EmptyState';
import Icon from '../../ui/Icon';
import LineItems from '../../ui/LineItems';
import Notice from '../../ui/Notice';
import PageHead from '../../ui/PageHead';
import Pager from '../../ui/Pager';
import Spinner from '../../ui/Spinner';
import StatusFilterBar from '../../ui/StatusFilterBar';
import StatusPill from '../../ui/StatusPill';

const NEXT_MOVE = {
  ASSIGNED: { to: 'OUT_FOR_DELIVERY', label: 'Picked up — start the ride' },
  OUT_FOR_DELIVERY: { to: 'DELIVERED', label: 'Handed over — mark delivered' },
};

function DropCard({ drop, busy, onAdvance }) {
  const move = NEXT_MOVE[drop.status];
  const customer = drop.customer ?? {};
  return (
    <article className="drop">
      <header className="ticket-head">
        <div>
          <span className="ticket-title">{drop.restaurant_name}</span>
          <span className="subtle">
            #{drop.id} · updated {formatWhen(drop.updated_at)}
          </span>
        </div>
        <StatusPill value={drop.status} />
      </header>

      <dl className="drop-facts">
        <div>
          <dt>Drop at</dt>
          <dd>
            <Icon name="pin" size={15} /> {drop.delivery_address}
          </dd>
        </div>
        <div>
          <dt>For</dt>
          <dd>{customer.name || '—'}</dd>
        </div>
        <div>
          <dt>Call</dt>
          <dd>
            {customer.phone ? (
              <a href={`tel:${customer.phone}`}>
                <Icon name="phone" size={15} /> {customer.phone}
              </a>
            ) : (
              '—'
            )}
          </dd>
        </div>
      </dl>

      <LineItems items={drop.items} compact />

      <footer className="ticket-foot">
        <strong>{formatPrice(drop.total_amount)}</strong>
        {move && (
          <button type="button" className="btn btn-primary" disabled={busy} onClick={() => onAdvance(drop, move.to)}>
            {move.label}
          </button>
        )}
      </footer>
    </article>
  );
}

export default function CourierBoard() {
  const [filters, setFilters] = useState({});
  const [page, setPage] = useState(1);
  const drops = useRemote(() => listAssignedDrops({ status: filters.status, page, page_size: 8 }), [filters, page]);
  const action = useAction(drops.refetch);

  return (
    <div className="page">
      <PageHead eyebrow="Rider" title="Active drops" lead="Orders handed to you. Ongoing ones show by default.">
        <button type="button" className="btn btn-quiet btn-small" onClick={drops.refetch}>
          <Icon name="refresh" size={16} /> Refresh
        </button>
      </PageHead>

      <StatusFilterBar
        value={filters}
        statuses={COURIER_STATUSES}
        withDates={false}
        onChange={(next) => {
          setFilters(next);
          setPage(1);
        }}
      />
      <Notice onRetry={drops.error ? drops.refetch : undefined}>{drops.error || action.error}</Notice>

      {drops.firstLoad ? (
        <Spinner label="Checking for drops…" />
      ) : drops.data?.items.length ? (
        <div className="drop-grid">
          {drops.data.items.map((drop) => (
            <DropCard
              key={drop.id}
              drop={drop}
              busy={action.busyKey === drop.id}
              onAdvance={(d, status) => action.run(d.id, () => updateDropStatus(d.id, status))}
            />
          ))}
        </div>
      ) : (
        !drops.error && (
          <EmptyState icon="bike" title="Nothing to deliver">
            Take a breather — new drops will appear here when a kitchen assigns you.
          </EmptyState>
        )
      )}

      <Pager result={drops.data} onPage={setPage} />
    </div>
  );
}
