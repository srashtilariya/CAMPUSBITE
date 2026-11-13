import { Link } from 'react-router-dom';
import { formatWhen } from '../../lib/format';
import { useAction } from '../../lib/useAction';
import { useRemote } from '../../lib/useRemote';
import { dismissReminder, listReminders, rescanReminders } from '../../services/kitchen';
import Icon from '../../ui/Icon';
import Notice from '../../ui/Notice';

/** Orders that have been sitting too long. `onChange` lets the parent refresh its stats too. */
export default function ReminderPanel({ onChange }) {
  const reminders = useRemote(() => listReminders({ page_size: 10 }), []);
  const action = useAction(async () => {
    await reminders.refetch();
    onChange?.();
  });

  const items = reminders.data?.items ?? [];
  const total = reminders.data?.total ?? 0;

  return (
    <section className="panel reminder-panel">
      <div className="panel-title-row">
        <h2 className="panel-title">
          <Icon name="bell" /> Needs attention
          {total > 0 && <span className="counter">{total}</span>}
        </h2>
        <button
          type="button"
          className="btn btn-quiet btn-small"
          disabled={action.busyKey === 'scan'}
          onClick={() => action.run('scan', rescanReminders)}
        >
          <Icon name="refresh" size={15} /> {action.busyKey === 'scan' ? 'Scanning…' : 'Scan again'}
        </button>
      </div>
      <Notice>{reminders.error || action.error}</Notice>
      {items.length === 0 ? (
        <p className="subtle">Nothing is stuck. Every open order is moving along.</p>
      ) : (
        <ul className="reminders">
          {items.map((reminder) => (
            <li key={reminder.id}>
              <Link to={`/orders/${reminder.order_id}`}>
                <span>{reminder.message}</span>
                <small className="subtle">{formatWhen(reminder.created_at)}</small>
              </Link>
              <button
                type="button"
                className="icon-button"
                aria-label="Dismiss reminder"
                disabled={action.busyKey === reminder.id}
                onClick={() => action.run(reminder.id, () => dismissReminder(reminder.id))}
              >
                <Icon name="close" size={16} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
