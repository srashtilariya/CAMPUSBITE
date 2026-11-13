import { useCallback, useState } from 'react';
import { describeError } from '../services/http';

/**
 * Wraps a one-off mutation (cancel, approve, toggle…) with busy + error state.
 * `run(key, task)` — `key` lets lists show a spinner on the right row.
 */
export function useAction(onSuccess) {
  const [busyKey, setBusyKey] = useState(null);
  const [error, setError] = useState('');

  const run = useCallback(
    async (key, task) => {
      setBusyKey(key);
      setError('');
      try {
        const result = await task();
        await onSuccess?.(result);
        return result;
      } catch (err) {
        setError(describeError(err));
        return undefined;
      } finally {
        setBusyKey(null);
      }
    },
    [onSuccess],
  );

  return { run, busyKey, error, clearError: () => setError('') };
}
