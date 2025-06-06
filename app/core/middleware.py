# app/core/middleware.py

import time
from fastapi import Request
from starlette.responses import Response

class LogRequestMiddleware:

    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        response: Response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.3f}s"
        print(f"{request.method} {request.url.path} completed in {process_time:.3f}s")
        return response
