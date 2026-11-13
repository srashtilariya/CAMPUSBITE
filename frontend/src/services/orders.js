import { get, post, withoutBlanks } from './http';

export const placeOrder = (payload) => post('/orders', payload);

export const listMyOrders = (query) => get('/orders/my', withoutBlanks(query));

export const getOrder = (orderId) => get(`/orders/${orderId}`);

export const cancelOrder = (orderId) => post(`/orders/${orderId}/cancel`);

export const reviewOrder = (orderId, { rating, comment }) =>
  post(`/orders/${orderId}/review`, { rating, comment });

export const requestRefund = (orderId, reason) => post(`/orders/${orderId}/return`, { reason });
