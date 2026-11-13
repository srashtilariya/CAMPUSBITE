import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { describeError } from '../../services/http';
import { landingFor, useSession } from '../../state/SessionProvider';
import Notice from '../../ui/Notice';
import AuthLayout from './AuthLayout';

const ROLE_OPTIONS = [
  { value: 'customer', title: 'Student', blurb: 'Order food to your door' },
  { value: 'restaurant_owner', title: 'Restaurant', blurb: 'List your kitchen' },
  { value: 'delivery_partner', title: 'Rider', blurb: 'Deliver orders' },
];

const BLANK = { role: 'customer', name: '', email: '', password: '', phone: '', address: '', restaurant_name: '' };

export default function SignUp() {
  const { signUp } = useSession();
  const navigate = useNavigate();
  const [draft, setDraft] = useState(BLANK);
  const [busy, setBusy] = useState(false);
  const [problem, setProblem] = useState('');

  const bind = (key) => ({
    value: draft[key],
    onChange: (event) => setDraft((d) => ({ ...d, [key]: event.target.value })),
  });

  const isOwner = draft.role === 'restaurant_owner';
  const isRider = draft.role === 'delivery_partner';

  const onSubmit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setProblem('');
    // Leave out anything the person didn't fill in.
    const payload = {};
    for (const [key, value] of Object.entries(draft)) {
      if (value !== '') payload[key] = value;
    }
    try {
      const user = await signUp(payload);
      navigate(landingFor(user), { replace: true });
    } catch (err) {
      setProblem(describeError(err, 'Your account couldn’t be created.'));
      setBusy(false);
    }
  };

  return (
    <AuthLayout
      title="Create your account"
      intro="Takes less than a minute."
      footer={
        <>
          Have an account already? <Link to="/signin">Sign in instead</Link>
        </>
      }
    >
      <Notice>{problem}</Notice>
      <form className="stack" onSubmit={onSubmit}>
        <fieldset className="role-picker">
          <legend>I’m joining as</legend>
          {ROLE_OPTIONS.map((option) => (
            <label key={option.value} className={draft.role === option.value ? 'is-picked' : ''}>
              <input
                type="radio"
                name="role"
                value={option.value}
                checked={draft.role === option.value}
                onChange={(e) => setDraft((d) => ({ ...d, role: e.target.value }))}
              />
              <strong>{option.title}</strong>
              <small>{option.blurb}</small>
            </label>
          ))}
        </fieldset>

        {isOwner && (
          <label className="field">
            <span>Restaurant name</span>
            <input required placeholder="e.g. Quad Corner Café" {...bind('restaurant_name')} />
          </label>
        )}
        <label className="field">
          <span>Your name</span>
          <input required minLength={2} autoComplete="name" placeholder="First and last name" {...bind('name')} />
        </label>
        <div className="field-pair">
          <label className="field">
            <span>Email address</span>
            <input type="email" required autoComplete="email" placeholder="you@university.edu" {...bind('email')} />
          </label>
          <label className="field">
            <span>Phone <em>(optional)</em></span>
            <input type="tel" autoComplete="tel" placeholder="+91 …" {...bind('phone')} />
          </label>
        </div>
        <label className="field">
          <span>Password</span>
          <input
            type="password"
            required
            minLength={6}
            maxLength={72}
            autoComplete="new-password"
            placeholder="At least 6 characters"
            {...bind('password')}
          />
        </label>
        {!isRider && (
          <label className="field">
            <span>{isOwner ? 'Where is the restaurant?' : 'Where should we deliver?'} <em>(optional)</em></span>
            <input placeholder={isOwner ? 'Building, block or street' : 'Hostel, room number…'} {...bind('address')} />
          </label>
        )}
        <button className="btn btn-primary btn-block" disabled={busy}>
          {busy ? 'Setting things up…' : 'Create account'}
        </button>
      </form>
    </AuthLayout>
  );
}
