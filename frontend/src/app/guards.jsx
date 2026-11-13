import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { landingFor, useSession } from '../state/SessionProvider';

/** Only signed-in users, optionally restricted to certain roles. */
export function RequireRole({ allow }) {
  const { user } = useSession();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/signin" replace state={{ returnTo: location.pathname }} />;
  }
  if (allow && !allow.includes(user.role)) {
    return <Navigate to={landingFor(user)} replace />;
  }
  return <Outlet />;
}

/** Sign-in / sign-up pages make no sense once you are signed in. */
export function GuestOnly() {
  const { user } = useSession();
  return user ? <Navigate to={landingFor(user)} replace /> : <Outlet />;
}

export function StartRedirect() {
  const { user } = useSession();
  return <Navigate to={landingFor(user)} replace />;
}
