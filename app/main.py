from fastapi import FastAPI
from .database import engine
from . import models
from .routers import customers, service, product, variant, repair, items, login

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(customers.router)
app.include_router(service.router)
app.include_router(product.router)
app.include_router(variant.router)
app.include_router(repair.router)
app.include_router(items.router)
app.include_router(login.router)

#Routers -          customers.py,   service.py,     product.py,     variant.py,     repair.py,      items.py
#Table Schemas -    models.py
#Pydantic Schemas -          body.py,     response.py,    update.py
#Error handling -   status_code.py
#Token -            oauth2.py,     login.py
