import { humanize } from '../lib/format';
import { ORDER_ENDINGS, ORDER_FLOW, STEP_HINTS } from '../lib/statuses';
import Icon from './Icon';

function stepState(index, currentIndex) {
  if (index < currentIndex) return 'passed';
  if (index === currentIndex) return 'active';
  return 'upcoming';
}

export default function OrderTimeline({ status }) {
  if (ORDER_ENDINGS.includes(status)) {
    const copy =
      status === 'CANCELLED'
        ? 'This order was cancelled and won’t be prepared.'
        : 'This order was refunded. The money is on its way back.';
    return (
      <div className={`timeline-ended ended-${status.toLowerCase()}`}>
        <strong>{humanize(status)}</strong>
        <span>{copy}</span>
      </div>
    );
  }

  const currentIndex = ORDER_FLOW.indexOf(status);
  const progress = Math.max(0, currentIndex) / (ORDER_FLOW.length - 1);

  return (
    <div className="timeline" style={{ '--progress': progress }}>
      <div className="timeline-rail" aria-hidden="true">
        <div className="timeline-fill" />
      </div>
      <ol className="timeline-steps">
        {ORDER_FLOW.map((step, index) => {
          const state = stepState(index, currentIndex);
          return (
            <li key={step} className={`timeline-step is-${state}`} aria-current={state === 'active' ? 'step' : undefined}>
              <span className="timeline-node">
                {state === 'passed' ? <Icon name="check" size={13} /> : index + 1}
              </span>
              <span className="timeline-text">
                <strong>{humanize(step)}</strong>
                <small>{STEP_HINTS[step]}</small>
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
