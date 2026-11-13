import { get, post } from './http';

export const signIn = (email, password) => post('/auth/login', { email, password });

export const signUp = (payload) => post('/auth/register', payload);

export const fetchProfile = () => get('/auth/me');
