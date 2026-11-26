# Módulo 2: Catálogo y Gestión de Productos (Online Retail II)

## Responsabilidad
Proveer el catálogo de productos, búsqueda por texto, filtrado por categoría y disponibilidad, consulta de detalle de producto y verificación de stock/precio para el resto de la aplicación.

## Estructura del Módulo

### Backend (`backend/app/modules/catalogo/`)
- `data/productos.json`: dataset sintético de productos del catálogo.
- `schemas.py`: modelos Pydantic (`Producto`, `RespuestaCatalogo`).
- `service.py`: lectura de datos, filtros, búsqueda, categorías y consulta de disponibilidad.
- `router.py`: rutas expuestas bajo el prefijo `/catalogo`.

### Frontend (`frontend/src/modules/catalogo/`)
- `api.js`: funciones de consumo HTTP hacia `/catalogo`.
- `components/FiltrosCatalogo.jsx`: búsqueda, selector de categoría y filtro de disponibilidad.
- `components/TarjetaProducto.jsx`: tarjeta visual por producto.
- `components/DetalleProducto.jsx`: modal de detalle y consulta de cantidad disponible.
- `pages/CatalogoPage.jsx`: vista principal que integra el módulo.
- `catalogo.css`: estilos del catálogo.
- `index.js`: punto de exportación del módulo.

## Endpoints Principales
- `GET /catalogo/productos` — Query params: `busqueda`, `categoria`, `solo_disponibles`.
- `GET /catalogo/categorias` — Lista de categorías disponibles.
- `GET /catalogo/productos/{producto_id}` — Detalle de un producto.
- `GET /catalogo/productos/{producto_id}/disponibilidad?cantidad=1` — Verifica stock y precio para la cantidad solicitada.

## Ejecución Local
1. **Backend** (desde `backend/`):
   ```powershell
   python -m pytest
   python -m uvicorn app.main:app --reload