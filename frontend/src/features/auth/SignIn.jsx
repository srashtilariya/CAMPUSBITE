import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { describeError } from '../../services/http';
import { landingFor, useSession } from '../../state/SessionProvider';
import Notice from '../../ui/Notice';
import AuthLayout from './AuthLayout';
import { DEMO_ACCOUNTS, DEMO_PASSWORD } from './demoAccounts';

export default function SignIn() {
  const { signIn } = useSession();
  const navigate = useNavigate();
  const { state } = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [pending, setPending] = useState(null); // 'form' or a demo email
  const [problem, setProblem] = useState('');

  const attempt = async (who, emailToUse, passwordToUse) => {
    setPending(who);
    setProblem('');
    try {
      const user = await signIn(emailToUse, passwordToUse);
      const returnTo = state?.returnTo;
      navigate(returnTo && returnTo !== '/signin' ? returnTo : landingFor(user), { replace: true });
    } catch (err) {
      setProblem(describeError(err, 'We couldn’t sign you in.'));
      setPending(null);
    }
  };

  const onSubmit = (event) => {
    event.preventDefault();
    attempt('form', email.trim(), password);
  };

  return (
    <AuthLayout
      title="Sign in"
      intro="Good to see you again. Pick up where you left off."
      footer={
        <>
          First time here? <Link to="/signup">Make an account</Link>
        </>
      }
    >
      <Notice>{problem}</Notice>
      <form className="stack" onSubmit={onSubmit}>
        <label className="field">
          <span>Email address</span>
          <input
            type="email"
            autoComplete="email"
            placeholder="you@university.edu"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
        <label className="field">
          <span>Password</span>
          <input
            type="password"
            autoComplete="current-password"
            placeholder="Your password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        <button className="btn btn-primary btn-block" disabled={pending !== null}>
          {pending === 'form' ? 'Checking…' : 'Continue'}
        </button>
      </form>

      <section className="demo-panel" aria-label="Demo accounts">
        <header>
          <strong>Just looking around?</strong>
          <span className="subtle">Jump in with a demo account — one click, no typing.</span>
        </header>
        {DEMO_ACCOUNTS.map(({ group, role, people }) => (
          <div key={group} className="demo-group">
            <span className={`demo-label role-${role}`}>{group}</span>
            <div className="demo-buttons">
              {people.map(({ local, email: demoEmail }) => (
                <button
                  type="button"
                  key={demoEmail}
                  className="demo-button"
                  title={demoEmail}
                  disabled={pending !== null}
                  onClick={() => attempt(demoEmail, demoEmail, DEMO_PASSWORD)}
                >
                  {pending === demoEmail ? '…' : local}
                </button>
              ))}
            </div>
          </div>
        ))}
        <small className="subtle">
          All demo accounts use <code>{DEMO_PASSWORD}</code>.
        </small>
      </section>
    </AuthLayout>
  );
}
