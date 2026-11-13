// Everything a restaurant owner can do lives under /owner on the API.
import { get, patch, post, put, remove, withoutBlanks } from './http';

// Restaurant profile
export const getMyRestaurant = () => get('/owner/restaurant');
export const updateMyRestaurant = (payload) => put('/owner/restaurant', payload);

// Menu
export const listDishes = (query) => get('/owner/menu', withoutBlanks(query));
export const createDish = (payload) => post('/owner/menu', payload);
export const updateDish = (dishId, payload) => put(`/owner/menu/${dishId}`, payload);
export const toggleDish = (dishId, isAvailable) =>
  patch(`/owner/menu/${dishId}/availability`, { is_available: isAvailable });
export const deleteDish = (dishId) => remove(`/owner/menu/${dishId}`);

// Orders
export const listKitchenOrders = (query) => get('/owner/orders', withoutBlanks(query));
export const moveOrder = (orderId, status) => patch(`/owner/orders/${orderId}/status`, { status });
export const listCouriers = () => get('/owner/delivery-partners');
export const assignCourier = (orderId, partnerId) =>
  post(`/owner/orders/${orderId}/assign`, { delivery_partner_id: partnerId });

// Insights
export const getKitchenStats = () => get('/owner/stats');

// Refund requests
export const listRefundRequests = (query) => get('/owner/returns', withoutBlanks(query));
export const approveRefund = (requestId, note) => post(`/owner/returns/${requestId}/approve`, { note });
export const rejectRefund = (requestId, note) => post(`/owner/returns/${requestId}/reject`, { note });

// Stale-order reminders
export const listReminders = (query) => get('/owner/reminders', query);
export const rescanReminders = () => post('/owner/reminders/refresh');
export const dismissReminder = (reminderId) => post(`/owner/reminders/${reminderId}/dismiss`);
