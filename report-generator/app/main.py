import uvicorn
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from handlers import limiter, router
from utils import session, close_db, args


def get_application() -> FastAPI:
    application = FastAPI()
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    application.add_middleware(SlowAPIMiddleware)
    application.state.limiter = limiter
    application.include_router(router=router)
    return application


app = get_application()

if args.ratelimit:
    print('Rate limits are on')
    app.state.limiter.enabled = True
else:
    app.state.limiter.enabled = False


# Before shutdown clear db and close session
@app.on_event('shutdown')
def shutdown_event():
    session.close()
    close_db()


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8080)
