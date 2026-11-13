"""LLM-backed Q&A over a single customer's order history."""
import json
import logging
import threading
import time
from collections import deque

from fastapi import HTTPException

from app.core.settings import load_config
from app.models import Order

log = logging.getLogger("campusbite.insights")

INSTRUCTIONS = (
    "You help a CampusBite customer understand their own food orders. Work strictly from the "
    "JSON you are given - it is the complete history for ONE customer. Prices are in Indian "
    "rupees (₹). Keep answers short and warm, prefer bullet points, and do arithmetic carefully. "
    "If the answer is not in the data, say you can't tell. Do not make up orders."
)
FALLBACK_QUESTION = "Summarise my order history briefly and point out anything interesting."


class SlidingWindowThrottle:
    """Allow at most ``limit`` calls per key within a rolling ``window`` seconds.

    Kept in process memory - fine for a single container, not for a fleet.
    """

    def __init__(self, limit: int, window: float = 60.0) -> None:
        self.limit = limit
        self.window = window
        self._calls: dict[int, deque[float]] = {}
        self._guard = threading.Lock()

    def hit(self, key: int) -> None:
        now = time.monotonic()
        with self._guard:
            calls = self._calls.setdefault(key, deque())
            horizon = now - self.window
            while calls and calls[0] < horizon:
                calls.popleft()
            if len(calls) < self.limit:
                calls.append(now)
                return
            wait = int(calls[0] + self.window - now) + 1
        raise HTTPException(
            status_code=429,
            detail=f"Too many AI requests. Try again in {wait} seconds.",
            headers={"Retry-After": str(wait)},
        )

    def reset(self) -> None:
        with self._guard:
            self._calls.clear()


throttle = SlidingWindowThrottle(load_config().insights_per_minute)


def _order_facts(order: Order) -> dict:
    return {
        "order_id": order.id,
        "restaurant": order.restaurant.name if order.restaurant else None,
        "placed_at": order.created_at.isoformat(),
        "status": order.status.value,
        "payment_status": order.payment_status.value,
        "return_status": order.return_status.value,
        "total": float(order.total_amount),
        "items": [
            {"name": line.name, "qty": line.quantity, "unit_price": float(line.unit_price)}
            for line in order.items
        ],
    }


def history_as_json(orders: list[Order]) -> str:
    return json.dumps([_order_facts(order) for order in orders], ensure_ascii=False)


def ask_model(orders: list[Order], question: str | None, today_iso: str) -> str:
    cfg = load_config()
    if not cfg.openai_key:
        raise HTTPException(status_code=503, detail="AI insights are not configured (missing OPENAI_API_KEY).")

    import openai  # imported lazily so the app boots fine without the key/SDK being exercised

    prompt = "\n".join(
        [
            f"Today's date (UTC): {today_iso}",
            "My orders, newest first (JSON):",
            history_as_json(orders),
            "",
            f"Question: {question or FALLBACK_QUESTION}",
        ]
    )
    client = openai.OpenAI(api_key=cfg.openai_key, timeout=30, max_retries=2)
    try:
        completion = client.chat.completions.create(
            model=cfg.openai_model,
            messages=[
                {"role": "system", "content": INSTRUCTIONS},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=600,
        )
    except openai.RateLimitError:
        log.warning("OpenAI is rate limiting us")
        raise HTTPException(status_code=429, detail="The AI service is busy right now. Please retry shortly.")
    except openai.AuthenticationError:
        log.error("OpenAI rejected our API key")
        raise HTTPException(status_code=503, detail="AI service authentication failed.")
    except openai.APIError as exc:
        log.error("OpenAI call failed: %s", exc)
        raise HTTPException(status_code=502, detail="The AI service returned an error. Please try again.")

    return (completion.choices[0].message.content or "").strip()
