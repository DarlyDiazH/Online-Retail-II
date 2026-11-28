# Cómo ejecutar el proyecto

Se necesitan dos programas instalados (una sola vez):

- **Python 3.11 o superior**: https://www.python.org/downloads/ (al instalar, marcar *Add python.exe to PATH*).
- **Node.js LTS**: https://nodejs.org

## 1. Backend (API)

1. Doble clic en `backend/iniciar_backend.bat`.
2. La primera vez crea `backend/.env`. Abrirlo y pegar en `DATABASE_URL` la cadena de conexión de Neon (Dashboard de Neon → *Connection string*). Cerrar la ventana y volver a abrir el `.bat`.
3. Queda en http://localhost:8000. La documentación interactiva está en http://localhost:8000/docs.

Sin `DATABASE_URL`, la API usa una base SQLite local: todo funciona, pero todos los usuarios quedan en el segmento **Nuevo**.

Por consola (cualquier sistema):

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## 2. Frontend (página)

1. Con el backend abierto, doble clic en `frontend/iniciar_frontend.bat`.
2. Se abre http://localhost:5173.

Por consola:

```bash
cd frontend
npm install
npm run dev
```

## 3. Probar el flujo completo

1. **Registrarse**. Para ver un descuento real, usar un `Customer_ID` que exista en Neon (ver `python probar_neon.py`); sin ID, la cuenta queda como **Nuevo**.
2. **Catálogo**: buscar, filtrar y abrir el detalle. Agregar productos al carrito.
3. **Carrito**: cambiar cantidades y ver el descuento del segmento.
4. **Confirmar pedido** → ver la confirmación y luego **Mis pedidos**.

## Pruebas automáticas

Doble clic en `backend/probar_backend.bat` (o `python -m pytest -v` dentro de `backend/`). El resultado queda en `backend/resultado_pruebas.txt`.

## Problemas comunes

| Problema | Solución |
|---|---|
| La página dice "No se pudo conectar con el servidor" | El backend no está abierto: abrir `iniciar_backend.bat`. |
| Todos los usuarios salen como "Nuevo" | Falta `DATABASE_URL` de Neon en `backend/.env`, o el usuario se registró sin `Customer_ID`. |
| `npm` no se reconoce | Instalar Node.js y abrir de nuevo el `.bat`. |
| Error de CORS | Abrir la página en `http://localhost:5173`. Si se usa otra dirección, agregarla en `FRONTEND_ORIGIN` del `.env` (separadas por comas). |
