import { Link } from 'react-router-dom';

const PERKS = [
  ['Order from every campus kitchen', 'One basket, live status, no queueing at the counter.'],
  ['Run your restaurant', 'Menu, order queue, refunds and reminders in one place.'],
  ['Ride and earn', 'See your assigned drops and mark them off as you go.'],
];

export default function AuthLayout({ title, intro, children, footer }) {
  return (
    <div className="auth">
      <aside className="auth-aside">
        <Link to="/restaurants" className="brand brand-light">
          <img src="/favicon.svg" alt="" width="34" height="34" />
          <span>
            campus<b>bite</b>
          </span>
        </Link>
        <div className="auth-pitch">
          <h2>Food from the quad, sorted.</h2>
          <ul>
            {PERKS.map(([heading, text]) => (
              <li key={heading}>
                <strong>{heading}</strong>
                <span>{text}</span>
              </li>
            ))}
          </ul>
        </div>
        <small>Built as a portfolio project · payments are simulated</small>
      </aside>

      <main className="auth-main">
        <div className="auth-panel">
          <h1>{title}</h1>
          {intro && <p className="lead">{intro}</p>}
          {children}
          {footer && <p className="auth-footer">{footer}</p>}
        </div>
      </main>
    </div>
  );
}
