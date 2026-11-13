import { get, withoutBlanks } from './http';

export const listRestaurants = (query) => get('/restaurants', withoutBlanks(query));

export const getRestaurant = (restaurantId) => get(`/restaurants/${restaurantId}`);

export const getRestaurantMenu = (restaurantId, query) =>
  get(`/restaurants/${restaurantId}/menu`, withoutBlanks(query));

export const getRestaurantReviews = (restaurantId, query) =>
  get(`/restaurants/${restaurantId}/reviews`, query);
