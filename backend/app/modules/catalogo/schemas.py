from pydantic import BaseModel, Field


class Producto(BaseModel):
    id: str = Field(..., examples=["PROD-001"])
    stock_code: str = Field(..., examples=["85123A"])
    nombre: str = Field(..., examples=["Lámpara Decorativa Vintage Blanca"])
    descripcion: str
    categoria: str = Field(..., examples=["Hogar y Decoración"])
    precio: float = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    disponible: bool
    imagen_url: str


class RespuestaCatalogo(BaseModel):
    total: int
    productos: list[Producto]