"""Punto de entrada del backend.

Cada módulo registra aquí su router. Para agregar el de otro módulo:
    from app.modules.<modulo>.router import router as <modulo>_router
    app.include_router(<modulo>_router)
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.modules.auth.router import router as auth_router
from app.modules.carrito.router import router as carrito_router
from app.modules.catalogo.router import router as catalogo_router

app = FastAPI(title="Online Retail II - API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crea las tablas que falten (usuarios, carritos, pedidos...). No borra ni modifica las existentes.
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(carrito_router)
app.include_router(catalogo_router)


@app.get("/")
def raiz():
    return {"estado": "ok", "docs": "/docs"}
