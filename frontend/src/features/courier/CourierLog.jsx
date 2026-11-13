import { useState } from 'react';
import { formatPrice, formatWhen } from '../../lib/format';
import { useRemote } from '../../lib/useRemote';
import { listCompletedDrops } from '../../services/courier';
import EmptyState from '../../ui/EmptyState';
import Notice from '../../ui/Notice';
import PageHead from '../../ui/PageHead';
import Pager from '../../ui/Pager';
import Spinner from '../../ui/Spinner';
import StatusPill from '../../ui/StatusPill';

export default function CourierLog() {
  const [page, setPage] = useState(1);
  const log = useRemote(() => listCompletedDrops({ page, page_size: 10 }), [page]);

  return (
    <div className="page">
      <PageHead eyebrow="Rider" title="Past drops" lead="Every delivery you’ve wrapped up." />
      <Notice onRetry={log.refetch}>{log.error}</Notice>

      {log.firstLoad ? (
        <Spinner label="Loading your log…" />
      ) : log.data?.items.length ? (
        <div className="panel panel-flush">
          <table className="grid-table">
            <thead>
              <tr>
                <th>#</th>
                <th>From</th>
                <th>To</th>
                <th>Address</th>
                <th className="num">Value</th>
                <th>Result</th>
                <th>Finished</th>
              </tr>
            </thead>
            <tbody>
              {log.data.items.map((drop) => (
                <tr key={drop.id}>
                  <td data-label="#">{drop.id}</td>
                  <td data-label="From">{drop.restaurant_name}</td>
                  <td data-label="To">{drop.customer?.name ?? '—'}</td>
                  <td data-label="Address">{drop.delivery_address}</td>
                  <td data-label="Value" className="num">
                    {formatPrice(drop.total_amount)}
                  </td>
                  <td data-label="Result">
                    <StatusPill value={drop.status} />
                  </td>
                  <td data-label="Finished">{formatWhen(drop.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        !log.error && (
          <EmptyState icon="clock" title="No finished drops yet">
            Completed deliveries will be listed here.
          </EmptyState>
        )
      )}

      <Pager result={log.data} onPage={setPage} />
    </div>
  );
}
