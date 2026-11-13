"""ORM -> response-model conversion for the pieces that need joined/derived fields."""
from app.models import Order, ReturnClaim, Review
from app.schemas.accounts import Contact
from app.schemas.catalog import ReviewView
from app.schemas.orders import OrderFull, OrderSummary, ReturnQueueItem


def _restaurant_name(order: Order) -> str | None:
    return order.restaurant.name if order.restaurant else None


def _contact(account) -> Contact | None:
    return None if account is None else Contact.model_validate(account)


def present_review(review: Review) -> ReviewView:
    author = review.customer.name if review.customer else None
    return ReviewView.model_validate(review).model_copy(update={"customer_name": author})


def present_order(order: Order) -> OrderSummary:
    return OrderSummary.model_validate(order).model_copy(
        update={"restaurant_name": _restaurant_name(order), "has_review": order.review is not None}
    )


def present_order_full(order: Order) -> OrderFull:
    review = order.review
    return OrderFull.model_validate(order).model_copy(
        update={
            "restaurant_name": _restaurant_name(order),
            "customer": _contact(order.customer),
            "delivery_partner": _contact(order.delivery_partner),
            "review": present_review(review) if review else None,
            "has_review": review is not None,
        }
    )


def present_return(claim: ReturnClaim) -> ReturnQueueItem:
    order = claim.order
    customer = order.customer if order else None
    return ReturnQueueItem.model_validate(claim).model_copy(
        update={
            "customer_name": customer.name if customer else None,
            "order_total": order.total_amount if order else None,
        }
    )
