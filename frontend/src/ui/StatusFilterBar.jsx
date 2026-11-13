import { humanize } from '../lib/format';
import { ALL_ORDER_STATUSES } from '../lib/statuses';

/**
 * Status + optional date range filter. `value` is a plain object of query params;
 * blank values are removed by the service layer before hitting the API.
 */
export default function StatusFilterBar({ value, onChange, statuses = ALL_ORDER_STATUSES, withDates = true }) {
  const update = (key) => (event) => onChange({ ...value, [key]: event.target.value });
  const active = Object.values(value).some(Boolean);

  return (
    <div className="toolbar">
      <div className="segmented" role="group" aria-label="Filter by status">
        <button type="button" className={!value.status ? 'is-on' : ''} onClick={() => onChange({ ...value, status: '' })}>
          Everything
        </button>
        {statuses.map((status) => (
          <button
            type="button"
            key={status}
            className={value.status === status ? 'is-on' : ''}
            onClick={() => onChange({ ...value, status })}
          >
            {humanize(status)}
          </button>
        ))}
      </div>
      {withDates && (
        <div className="toolbar-dates">
          <label className="field-inline">
            <span>Since</span>
            <input type="date" value={value.date_from || ''} onChange={update('date_from')} />
          </label>
          <label className="field-inline">
            <span>Until</span>
            <input type="date" value={value.date_to || ''} onChange={update('date_to')} />
          </label>
        </div>
      )}
      {active && (
        <button type="button" className="link-button" onClick={() => onChange({})}>
          Reset filters
        </button>
      )}
    </div>
  );
}
