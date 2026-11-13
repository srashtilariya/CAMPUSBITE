import { useEffect, useState } from 'react';

export function useDebouncedValue(value, wait = 300) {
  const [settled, setSettled] = useState(value);

  useEffect(() => {
    const timer = window.setTimeout(() => setSettled(value), wait);
    return () => window.clearTimeout(timer);
  }, [value, wait]);

  return settled;
}
