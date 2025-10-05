import structlog, uuid, time
from starlette.types import ASGIApp, Receive, Scope, Send

SENSITIVE_KEYS = {"password", "authorization", "token", "access_token", "refresh_token"}

def setup_logging():
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ]
    )
def redact_sensitive(_, __, event_dict):
    for k in list(event_dict.keys()):
        if k.lower() in SENSITIVE_KEYS:
            event_dict[k] = "[REDACTED]"
    return event_dict

class RequestIDMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send); return
        request_id = str(uuid.uuid4())
        start = time.time()
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.append((b"x-request-id", request_id.encode()))
            await send(message)
        logger = structlog.get_logger()
        logger.info("http_start", path=scope.get("path"), request_id=request_id)
        await self.app(scope, receive, send_wrapper)
        logger.info("http_end", path=scope.get("path"), request_id=request_id, duration_ms=int((time.time()-start)*1000))