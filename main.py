import uvicorn
from fastapi import FastAPI, Depends, Request
from starlette.middleware.cors import CORSMiddleware
# import staticfiles
from fastapi.staticfiles import StaticFiles

# app config (env variables)
from socials.config import settings

# routes importing
# from socials.apps.products import router as products_router
from socials.apps.users import router as users_router
# from socials.apps.orders import router as orders_router
# from socials.apps.cart import router as cart_router
# from socials.apps.coupons import router as coupons_router
from socials.apps.site import router as site_router
from socials.apps.bots import router as bots_router
from socials.apps.bots_tasks import router as bots_tasks_router

from socials.apps.cart.cart import create_session_id
# eof routes importing
from socials.dependencies import get_api_app_client

# import database
from socials.database.main_db import db_provider

# include all necessary routes
app = FastAPI(
    title="Flowers API backend",
    version="0.0.1",
    description="backend api endpoints for flowers app",
    dependencies=[Depends(get_api_app_client)]
)
# mount static files folder
app.mount("/static", StaticFiles(directory="static"), name = "static")

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    # allow_credentials=True,
    allow_methods = ['*'],
    allow_headers = ['*'],
)

# setting up app cors


# include app routes
# app.include_router(products_router.router)
app.include_router(users_router.router)
# app.include_router(orders_router.router)
# app.include_router(cart_router.router)
# app.include_router(coupons_router.router)
app.include_router(site_router.router)
app.include_router(bots_router.router)
app.include_router(bots_tasks_router.router)

@app.on_event('startup')
async def startup_db_client():
    print("startup db client")
    print('setting are', settings)
    pass


@app.on_event('shutdown')
async def shutdown_db_client():
    db_provider.db_client.close()




@app.get("/status")
def get_status(request: Request):
    """ Get status of server """
    print('request is', request)
    print(request.__dict__)
    return {
        "status": "running",
        }

@app.get("/session")
def create_session():
    """ Creates session id for client """
    session_key = create_session_id()
    return {
        "session_id": session_key,
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host='0.0.0.0',
        reload=settings.DEBUG_MODE,
        port=8000,
    )
