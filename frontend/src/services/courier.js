import { get, patch, withoutBlanks } from './http';

export const listAssignedDrops = (query) => get('/delivery/orders', withoutBlanks(query));

export const listCompletedDrops = (query) => get('/delivery/history', query);

export const updateDropStatus = (orderId, status) =>
  patch(`/delivery/orders/${orderId}/status`, { status });
