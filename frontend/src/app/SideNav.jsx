import { Link, NavLink, useNavigate } from 'react-router-dom';
import { firstName } from '../lib/format';
import { useBasket } from '../state/BasketProvider';
import { useSession } from '../state/SessionProvider';
import Icon from '../ui/Icon';
import { NAV_BY_ROLE, ROLE_TITLES } from './navigation';

function Brand() {
  return (
    <Link to="/" className="brand">
      <img src="/favicon.svg" alt="" width="30" height="30" />
      <span>
        campus<b>bite</b>
      </span>
    </Link>
  );
}

export default function SideNav({ open, onNavigate }) {
  const { user, signOut } = useSession();
  const { itemCount } = useBasket();
  const navigate = useNavigate();
  const entries = NAV_BY_ROLE[user?.role ?? 'guest'];

  const leave = () => {
    signOut();
    onNavigate();
    navigate('/signin');
  };

  return (
    <aside className={`sidenav ${open ? 'is-open' : ''}`}>
      <div className="sidenav-top">
        <Brand />
        {user && <span className="role-tag">{ROLE_TITLES[user.role]}</span>}
      </div>

      <nav className="sidenav-links" aria-label="Main">
        {entries.map(([to, text, icon]) => (
          <NavLink key={to} to={to} end onClick={onNavigate}>
            <Icon name={icon} />
            <span>{text}</span>
          </NavLink>
        ))}
        {user?.role === 'customer' && (
          <NavLink to="/basket" onClick={onNavigate}>
            <Icon name="bag" />
            <span>Basket</span>
            {itemCount > 0 && <span className="counter">{itemCount}</span>}
          </NavLink>
        )}
      </nav>

      <div className="sidenav-foot">
        {user ? (
          <>
            <div className="who">
              <span className="avatar">{firstName(user.name).charAt(0).toUpperCase()}</span>
              <span>
                <strong>{user.name}</strong>
                <small>{user.email}</small>
              </span>
            </div>
            <button type="button" className="btn btn-quiet btn-block" onClick={leave}>
              <Icon name="logout" /> Sign out
            </button>
          </>
        ) : (
          <>
            <Link to="/signin" className="btn btn-primary btn-block" onClick={onNavigate}>
              <Icon name="login" /> Sign in
            </Link>
            <Link to="/signup" className="btn btn-quiet btn-block" onClick={onNavigate}>
              Create an account
            </Link>
          </>
        )}
      </div>
    </aside>
  );
}

export { Brand };
