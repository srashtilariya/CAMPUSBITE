import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { signIn, signUp } from '../services/auth';
import { SESSION_EXPIRED_EVENT } from '../services/http';
import { clearSession, readStoredUser, saveSession } from './storage';

const SessionContext = createContext(null);

/** Where each role lands after signing in. */
export const LANDING_BY_ROLE = {
  customer: '/restaurants',
  restaurant_owner: '/kitchen',
  delivery_partner: '/rides',
};

export const landingFor = (user) => (user ? LANDING_BY_ROLE[user.role] ?? '/' : '/restaurants');

export function SessionProvider({ children }) {
  const [user, setUser] = useState(readStoredUser);

  // The HTTP layer clears storage on a 401; we just mirror that in React state.
  useEffect(() => {
    const onExpired = () => setUser(null);
    window.addEventListener(SESSION_EXPIRED_EVENT, onExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, onExpired);
  }, []);

  const session = useMemo(() => {
    const adopt = (response) => {
      saveSession(response.access_token, response.user);
      setUser(response.user);
      return response.user;
    };

    return {
      user,
      isSignedIn: Boolean(user),
      signIn: async (email, password) => adopt(await signIn(email, password)),
      signUp: async (payload) => adopt(await signUp(payload)),
      signOut: () => {
        clearSession();
        setUser(null);
      },
    };
  }, [user]);

  return <SessionContext.Provider value={session}>{children}</SessionContext.Provider>;
}

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error('useSession must be used inside <SessionProvider>');
  return ctx;
}
