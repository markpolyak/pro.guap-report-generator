from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
import os

# 使用 Redis 存储
def create_limiter():
    # 使用环境变量配置存储
    storage_uri = os.getenv("REDIS_URL", "memory://")
    
    return Limiter(
        key_func=get_remote_address,
        default_limits=["5/minute"],
        storage_uri=storage_uri
    )

limiter = create_limiter()

def apply_rate_limit(app, enabled: bool = False):
    if enabled:
        # 确保中间件是第一个被执行的
        app.add_middleware(SlowAPIMiddleware)
        app.state.limiter = limiter
        
        # 添加异常处理
        @app.exception_handler(RateLimitExceeded)
        async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
            raise HTTPException(
                status_code=429, 
                detail="Too Many Requests",
                headers={"Retry-After": str(exc.retry_after)}
            )
        
