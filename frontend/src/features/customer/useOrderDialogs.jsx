import { useState } from 'react';
import RefundDialog from './RefundDialog';
import ReviewDialog from './ReviewDialog';

/** Shared open/close state for the review + refund dialogs. */
export function useOrderDialogs(onSaved) {
  const [open, setOpen] = useState(null); // { kind, order }

  const close = () => setOpen(null);

  let dialog = null;
  if (open?.kind === 'review') dialog = <ReviewDialog order={open.order} onDismiss={close} onSaved={onSaved} />;
  if (open?.kind === 'refund') dialog = <RefundDialog order={open.order} onDismiss={close} onSaved={onSaved} />;

  return {
    dialog,
    openReview: (order) => setOpen({ kind: 'review', order }),
    openRefund: (order) => setOpen({ kind: 'refund', order }),
  };
}

/** Which follow-up actions a customer has on an order. */
export function customerOptions(order, hasReview) {
  const delivered = order.status === 'DELIVERED';
  return {
    canCancel: order.status === 'PLACED',
    canReview: delivered && !hasReview,
    canRefund: delivered && order.return_status === 'none',
  };
}
