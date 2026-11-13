"""Plain ASGI middleware that times each request and stamps a request id on it.

Adds two response headers:
  * X-Request-ID   - echoed from the incoming request, or a fresh 12-char id
  * X-Process-Time - wall time spent inside the app, e.g. "4.2ms"
"""
import logging
import time
import uuid

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

log = logging.getLogger("campusbite.http")


class RequestTracer:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = Headers(scope=scope).get("X-Request-ID") or uuid.uuid4().hex[:12]
        scope.setdefault("state", {})["request_id"] = request_id
        method, path = scope["method"], scope["path"]
        started = time.perf_counter()
        status_seen: list[int] = []

        def elapsed_ms() -> float:
            return (time.perf_counter() - started) * 1000

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                took = elapsed_ms()
                status_seen.append(message["status"])
                headers = MutableHeaders(scope=message)
                headers["X-Process-Time"] = f"{took:.1f}ms"
                headers["X-Request-ID"] = request_id
                log.info("%s %s -> %s (%.1f ms) [%s]", method, path, message["status"], took, request_id)
            await send(message)

        try:
            await self.app(scope, receive, send_with_headers)
        except Exception:
            if not status_seen:
                log.exception("%s %s -> 500 (%.1f ms) [%s]", method, path, elapsed_ms(), request_id)
            raise
