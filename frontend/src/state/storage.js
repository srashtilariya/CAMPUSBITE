// Tiny wrapper around localStorage so keys live in one place.
const KEYS = {
  token: 'cb.auth.token',
  user: 'cb.auth.user',
  basket: 'cb.basket',
};

function readJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export const readToken = () => localStorage.getItem(KEYS.token);

export const readStoredUser = () => (readToken() ? readJson(KEYS.user, null) : null);

export function saveSession(token, user) {
  localStorage.setItem(KEYS.token, token);
  localStorage.setItem(KEYS.user, JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem(KEYS.token);
  localStorage.removeItem(KEYS.user);
}

export const readBasket = (fallback) => readJson(KEYS.basket, fallback);

export const writeBasket = (basket) => localStorage.setItem(KEYS.basket, JSON.stringify(basket));
