# Módulo 3: Carrito y proceso de compra

Responsable: Christian. Rama: `feature/carrito-compras`

Este módulo cubre el carrito, el resumen de compra con descuentos según el segmento, la confirmación del pedido (simulada, sin pagos reales) y el historial de compras.

## Archivos

```
backend/
  requirements.txt
  .env.example
  app/
    main.py                 # arranque de FastAPI (los demás módulos agregan aquí su router)
    database.py             # conexión a Neon (compartida)
    modules/carrito/
      descuentos.py         # beneficios por segmento (aquí se editan los %)
      calculos.py           # subtotal, descuento y total
      integraciones.py      # conexión con productos (Persona 2) y segmento (Persona 1)
      models.py             # tablas: carritos, carrito_items, pedidos, pedido_items
      schemas.py
      service.py            # reglas del carrito y del pedido
      router.py             # endpoints
      productos_ejemplo.json
  tests/test_calculos.py

frontend/src/modules/carrito/
  index.jsx                 # exporta CarritoProvider, rutasCarrito, BotonAgregar, IconoCarrito
  api.js                    # llamadas al backend
  CarritoContext.jsx        # estado global del carrito
  components/               # ResumenCompra, BotonAgregar, IconoCarrito, DetallePedido
  pages/                    # CarritoPage, ConfirmacionPage, HistorialPage
  carrito.css
```

## Cómo ejecutarlo

Backend (desde `backend/`):

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # y poner la DATABASE_URL de Neon
uvicorn app.main:app --reload
```

Documentación interactiva: http://localhost:8000/docs. Si no se pone `DATABASE_URL`, se usa un SQLite local para hacer pruebas.

Las tablas `carritos`, `carrito_items`, `pedidos` y `pedido_items` se crean solas en Neon la primera vez que arranca la API.

Pruebas de la lógica de precios: `python -m unittest -v`

Frontend (React + Vite): se necesita `react-router-dom`. Variables opcionales en `frontend/.env`:

```
VITE_API_URL=http://localhost:8000
VITE_MONEDA=GBP
```

## Endpoints

Todos reciben la cabecera `X-Usuario-Id` con el id del usuario que inició sesión.

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/api/carrito` | Carrito con líneas, subtotal, descuento, total, beneficio y avisos |
| POST | `/api/carrito/items` | Agrega un producto `{producto_id, cantidad}` |
| PUT | `/api/carrito/items/{producto_id}` | Cambia la cantidad `{cantidad}` (0 = eliminar) |
| DELETE | `/api/carrito/items/{producto_id}` | Elimina un producto |
| DELETE | `/api/carrito` | Vacía el carrito |
| POST | `/api/pedidos` | Confirma el pedido `{total_esperado}` y devuelve la confirmación |
| GET | `/api/pedidos` | Historial de compras |
| GET | `/api/pedidos/{codigo}` | Detalle de un pedido |

## Reglas de negocio

- El precio y el nombre siempre se toman del catálogo del servidor. El cliente solo envía el id y la cantidad.
- No se puede agregar más cantidad que el stock disponible.
- Al confirmar, el servidor vuelve a revisar el producto, el stock y el precio. Si algo cambió, el pedido no se crea (respuesta 409) y se devuelve el carrito actualizado para que el usuario lo revise.
- El descuento se calcula en el servidor con el segmento real del usuario en Neon. Si el total que vio el usuario no coincide, el pedido tampoco se crea.
- Si el usuario no tiene segmento, o el segmento no se reconoce, se le aplica el beneficio de **Nuevo**.
- El pedido guarda una copia de los precios, el segmento y el descuento de ese momento, así el historial no cambia aunque después cambie el catálogo.

### Beneficios por segmento (editables en `descuentos.py`)

| Segmento | Descuento | Condición |
|---|---|---|
| Campeones | 5 % | — |
| En riesgo | 15 % | compra mínima £100 |
| Prometedores | 10 % | compra mínima £50 |
| Perdidos | 20 % | compra mínima £150 |
| Nuevo (provisional) | 5 % | tope £20 |

> Los cuatro primeros corresponden a los segmentos del K-Means guardados en Neon. "Nuevo" es una categoría provisional.

## Integración con los otros módulos

**Persona 1 (autenticación):**
- Al iniciar sesión, guardar el id: `localStorage.setItem("usuario_id", id)`. También se puede cambiar `obtenerUsuarioId()` en `api.js` para que lo lea del token.
- En el backend, cambiar `usuario_actual` en `router.py` por la dependencia que valida el token.
- El segmento se lee con `SEGMENTO_SQL` (en `.env`). Hay que ajustarlo a la tabla y la columna reales, por ejemplo:
  `SELECT v.segmento FROM usuarios u JOIN vw_descuentos_checkout v ON v.customer_id = u.customer_id WHERE u.id = :usuario_id`

**Persona 2 (catálogo):**
- Poner el archivo de productos en `backend/data/productos.json` (o `.csv`), o cambiar `PRODUCTOS_PATH`. Se aceptan columnas en español o en inglés: `id`/`StockCode`, `nombre`/`Description`, `precio`/`Price`, `stock`, `categoria`, `imagen`.
- En las tarjetas de producto, agregar: `<BotonAgregar productoId={p.id} stock={p.stock} />`

**Quien arme `App.jsx`:**

```jsx
import { CarritoProvider, rutasCarrito, IconoCarrito } from "./modules/carrito";

<BrowserRouter>
  <CarritoProvider>
    <nav>… <IconoCarrito /></nav>
    <Routes>
      {rutasCarrito}
      {/* rutas de los otros módulos */}
    </Routes>
  </CarritoProvider>
</BrowserRouter>
```

Las pantallas del carrito enlazan a `/catalogo` y `/login`. Si esas rutas se llaman distinto, hay que ajustar los enlaces en las páginas del carrito.
