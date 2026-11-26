from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.catalogo.router import router as catalogo_router


app = FastAPI(
    title="Online Retail II - API",
    description="API modular de Online Retail II",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalogo_router)


@app.get("/")
def health_check():
    return {"status": "ok", "modulo": "catalogo"}