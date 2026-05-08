from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from services.signals import signal_service
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-backed rate limiting middleware to prevent API abuse.
    Focuses on protecting high-cost LLM and Vector search endpoints.
    """
    def __init__(self, app, limit: int = 10, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        # Only rate limit the recommendations endpoint
        if request.url.path.startswith("/api/v1/recommendations"):
            # Use client host if available, otherwise fallback to 127.0.0.1
            # (request.client can be None in certain testing environments)
            client_ip = request.client.host if request.client else "127.0.0.1"
            key = f"rate_limit:{client_ip}"
            
            # Use Redis to track requests
            # Note: We use the existing signal_service redis connection
            current = await signal_service.redis.get(key)
            
            if current and int(current) >= self.limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
            
            # Basic Prompt Injection Detection
            body = await request.body()
            if body:
                body_str = body.decode("utf-8", errors="ignore").lower()
                injection_patterns = ["ignore all previous", "system prompt", "you are an ai", "override"]
                if any(pattern in body_str for pattern in injection_patterns):
                    raise HTTPException(status_code=400, detail="Potential security threat detected in input.")

            # Increment and set expiry if new
            pipe = signal_service.redis.pipeline()
            await pipe.incr(key)
            await pipe.expire(key, self.window)
            await pipe.execute()

        response = await call_next(request)
        return response
