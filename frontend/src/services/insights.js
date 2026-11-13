import { post } from './http';

/** An empty question asks the backend for a general summary. */
export const askAboutOrders = (question) => post('/ai/insights', { question: question || null });
