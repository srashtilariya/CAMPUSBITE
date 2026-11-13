import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { readBasket, writeBasket } from './storage';

const MAX_PER_LINE = 50;
const EMPTY_BASKET = Object.freeze({ restaurant: null, lines: [] });

const BasketContext = createContext(null);

const clampQty = (qty) => Math.max(0, Math.min(qty, MAX_PER_LINE));

function loadBasket() {
  const saved = readBasket(null);
  // Accept only well-formed baskets; anything else starts fresh.
  if (saved && Array.isArray(saved.lines) && saved.lines.length) return saved;
  return EMPTY_BASKET;
}

export function BasketProvider({ children }) {
  const [basket, setBasket] = useState(loadBasket);

  useEffect(() => {
    writeBasket(basket);
  }, [basket]);

  /** True when adding from `restaurant` would wipe a basket from somewhere else. */
  const conflictsWith = useCallback(
    (restaurant) => Boolean(basket.restaurant && basket.restaurant.id !== restaurant.id),
    [basket.restaurant],
  );

  const addDish = useCallback((restaurant, dish) => {
    setBasket((current) => {
      const sameKitchen = current.restaurant?.id === restaurant.id;
      const lines = sameKitchen ? current.lines : [];
      const existing = lines.find((line) => line.id === dish.id);

      const nextLines = existing
        ? lines.map((line) => (line.id === dish.id ? { ...line, quantity: clampQty(line.quantity + 1) } : line))
        : [...lines, { id: dish.id, name: dish.name, price: Number(dish.price), quantity: 1 }];

      return { restaurant: { id: restaurant.id, name: restaurant.name }, lines: nextLines };
    });
  }, []);

  const setQuantity = useCallback((dishId, quantity) => {
    setBasket((current) => {
      const qty = clampQty(quantity);
      const lines = current.lines
        .map((line) => (line.id === dishId ? { ...line, quantity: qty } : line))
        .filter((line) => line.quantity > 0);
      return lines.length ? { ...current, lines } : EMPTY_BASKET;
    });
  }, []);

  const empty = useCallback(() => setBasket(EMPTY_BASKET), []);

  const value = useMemo(() => {
    let itemCount = 0;
    let subtotal = 0;
    for (const line of basket.lines) {
      itemCount += line.quantity;
      subtotal += line.quantity * line.price;
    }
    return {
      restaurant: basket.restaurant,
      lines: basket.lines,
      itemCount,
      subtotal,
      isEmpty: basket.lines.length === 0,
      conflictsWith,
      addDish,
      setQuantity,
      dropLine: (dishId) => setQuantity(dishId, 0),
      empty,
    };
  }, [basket, conflictsWith, addDish, setQuantity, empty]);

  return <BasketContext.Provider value={value}>{children}</BasketContext.Provider>;
}

export function useBasket() {
  const ctx = useContext(BasketContext);
  if (!ctx) throw new Error('useBasket must be used inside <BasketProvider>');
  return ctx;
}
