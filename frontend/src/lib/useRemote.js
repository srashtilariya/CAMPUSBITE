import { useCallback, useEffect, useRef, useState } from 'react';
import { describeError } from '../services/http';

/**
 * Fetch something whenever `deps` change.
 * Late responses from superseded requests are ignored.
 */
export function useRemote(fetcher, deps) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const ticket = useRef(0);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const refetch = useCallback(async () => {
    const mine = ++ticket.current;
    setLoading(true);
    setError('');
    try {
      const result = await fetcher();
      if (mine === ticket.current) setData(result);
    } catch (err) {
      if (mine === ticket.current) setError(describeError(err));
    } finally {
      if (mine === ticket.current) setLoading(false);
    }
  }, deps);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, loading, error, refetch, firstLoad: loading && data === null };
}
