"""AI order insights for customers - scoped strictly to the caller's own orders."""
from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session, selectinload

from app.api.auth_guards import customer_only
from app.core.clock import now_utc
from app.core.db import db_session
from app.core.settings import load_config
from app.domain import insights_engine
from app.models import Account, Order
from app.schemas.insights import InsightAnswer, InsightQuestion

router = APIRouter(prefix="/ai", tags=["AI Insights"])

HISTORY_WINDOW = 50  # most recent orders sent to the model
NO_ORDERS_REPLY = (
    "You haven't placed any orders yet, so there's nothing to analyse. Place an order and come back!"
)


@router.post("/insights", response_model=InsightAnswer)
async def ask_about_my_orders(
    body: InsightQuestion, me: Account = Depends(customer_only), db: Session = Depends(db_session)
):
    insights_engine.throttle.hit(me.id)
    model_name = load_config().openai_model

    recent = (
        db.query(Order)
        .options(selectinload(Order.items), selectinload(Order.restaurant))
        .filter(Order.customer_id == me.id)
        .order_by(Order.created_at.desc())
        .limit(HISTORY_WINDOW)
        .all()
    )
    if not recent:
        return InsightAnswer(answer=NO_ORDERS_REPLY, orders_considered=0, model=model_name)

    today = now_utc().date().isoformat()
    answer = await run_in_threadpool(insights_engine.ask_model, recent, body.question, today)
    return InsightAnswer(answer=answer, orders_considered=len(recent), model=model_name)
