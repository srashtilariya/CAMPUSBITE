/** The happy path an order walks through, in order. */
export const ORDER_FLOW = ['PLACED', 'ACCEPTED', 'PREPARING', 'READY', 'ASSIGNED', 'OUT_FOR_DELIVERY', 'DELIVERED'];

export const ORDER_ENDINGS = ['CANCELLED', 'REFUNDED'];

export const ALL_ORDER_STATUSES = [...ORDER_FLOW, ...ORDER_ENDINGS];

export const IN_PROGRESS = ORDER_FLOW.filter((s) => s !== 'DELIVERED');

export const COURIER_STATUSES = ['ASSIGNED', 'OUT_FOR_DELIVERY', 'DELIVERED', 'REFUNDED'];

/** Short descriptions shown under each timeline step. */
export const STEP_HINTS = {
  PLACED: 'We sent it to the kitchen',
  ACCEPTED: 'The kitchen said yes',
  PREPARING: 'Your food is being made',
  READY: 'Packed and waiting',
  ASSIGNED: 'A rider is on the way to pick up',
  OUT_FOR_DELIVERY: 'Heading to you',
  DELIVERED: 'Enjoy your meal',
};

/** Colour family for each status-ish value, used by <StatusPill>. */
const TONES = {
  PLACED: 'blue',
  ACCEPTED: 'teal',
  PREPARING: 'amber',
  READY: 'violet',
  ASSIGNED: 'rose',
  OUT_FOR_DELIVERY: 'orange',
  DELIVERED: 'green',
  CANCELLED: 'red',
  REFUNDED: 'slate',
  mock_paid: 'green',
  pending: 'amber',
  refunded: 'slate',
  requested: 'amber',
  approved: 'green',
  rejected: 'red',
};

export const toneOf = (value) => TONES[value] ?? 'slate';
