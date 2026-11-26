# Módulo 1: Registro, autenticación y perfil de clientes

Responsable: Darly. Rama: `feature/autenticacion`

## Alcance y decisiones

- Registro, inicio de sesión y perfil con el comportamiento de una aplicación normal (validaciones, mensajes de error, sesión que persiste, rutas protegidas, cerrar sesión).
- Las contraseñas se guardan con **hash bcrypt**, nunca en texto plano.
- **Identificación sin tokens (alcance académico):** al iniciar sesión el frontend guarda el id del usuario en `localStorage["usuario_id"]` y lo envía en la cabecera `X-Usuario-Id`, que es el contrato que ya usa el módulo de carrito. No se implementan JWT ni protección contra suplantación.
- Los segmentos se leen del modelo K-Means; no se inventan clústeres. Quien no tiene coincidencia histórica queda en la categoría comercial provisional **Nuevo**.

## Identificadores

| Elemento | Significado |
|---|---|
| `user_id` (`usuarios.id`) | Cuenta creada en la aplicación |
| `Customer_ID` (`usuarios.customer_id`) | ID histórico de Online Retail II. Vacío = sin coincidencia |
| `segmento` | Se consulta en la tabla de clientes (no se guarda en `usuarios`) |

## Archivos

```
backend/app/modules/auth/   models.py  schemas.py  service.py  router.py  seguridad.py
backend/tests/test_auth.py
frontend/src/modules/auth/  index.jsx  api.js  AuthContext.jsx  auth.css
                            pages/ (Login, Registro, Perfil)  components/ (RutaProtegida, MenuUsuario)
```

Cambios mínimos en archivos compartidos: `main.py` (registrar el router), `requirements.txt` (`bcrypt`), `.env.example` (`SEGMENTO_SQL` y `CLIENTE_SQL`), `tests/test_api.py` (la tabla de prueba ya no se llama `usuarios`).

## Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/api/auth/registro` | Crea la cuenta (`nombre`, `correo`, `contrasena`, `customer_id` opcional) y devuelve el perfil |
| POST | `/api/auth/login` | Valida credenciales y devuelve el perfil |
| GET | `/api/auth/perfil` | Perfil con segmento y beneficio (cabecera `X-Usuario-Id`) |

## Pendiente de acordar con el equipo

- El segmento y el ID de cliente se consultan en la vista `vw_descuentos_checkout` de Neon.
- Confirmar con el equipo el beneficio de **Nuevo** (5 %, tope £20), que no viene del K-Means.
