// Cliente HTTP del módulo de carrito.
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// El módulo de autenticación (Persona 1) debe guardar el id del usuario al iniciar
// sesión: localStorage.setItem("usuario_id", id). Si cambia la forma (token, contexto),
// solo hay que ajustar esta función.
export function obtenerUsuarioId() {
  return localStorage.getItem("usuario_id");
}

export class ErrorApi extends Error {
  constructor(estado, mensaje, detalle) {
    super(mensaje);
    this.estado = estado;
    this.detalle = detalle ?? {};
  }
}

async function pedir(ruta, { method = "GET", body } = {}) {
  const usuarioId = obtenerUsuarioId();
  if (!usuarioId) throw new ErrorApi(401, "Debes iniciar sesión para usar el carrito.");

  let resp;
  try {
    resp = await fetch(`${API_URL}${ruta}`, {
      method,
      headers: { "Content-Type": "application/json", "X-Usuario-Id": usuarioId },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ErrorApi(0, "No se pudo conectar con el servidor.");
  }

  const datos = await resp.json().catch(() => null);
  if (!resp.ok) {
    const d = datos?.detail;
    const mensaje =
      (typeof d === "string" && d) || d?.mensaje ||
      (Array.isArray(d) && "Datos inválidos.") || "Ocurrió un error.";
    throw new ErrorApi(resp.status, mensaje, typeof d === "object" ? d : {});
  }
  return datos;
}

export const apiCarrito = {
  ver: () => pedir("/api/carrito"),
  agregar: (productoId, cantidad = 1) =>
    pedir("/api/carrito/items", { method: "POST", body: { producto_id: String(productoId), cantidad } }),
  cambiarCantidad: (productoId, cantidad) =>
    pedir(`/api/carrito/items/${encodeURIComponent(productoId)}`, { method: "PUT", body: { cantidad } }),
  eliminar: (productoId) =>
    pedir(`/api/carrito/items/${encodeURIComponent(productoId)}`, { method: "DELETE" }),
  vaciar: () => pedir("/api/carrito", { method: "DELETE" }),
  confirmar: (totalEsperado) =>
    pedir("/api/pedidos", { method: "POST", body: { total_esperado: totalEsperado } }),
  historial: () => pedir("/api/pedidos"),
  pedido: (codigo) => pedir(`/api/pedidos/${encodeURIComponent(codigo)}`),
};

const formato = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: import.meta.env.VITE_MONEDA ?? "GBP",
  currencyDisplay: "narrowSymbol", // £ en vez de "GBP"
});
export const dinero = (valor) => formato.format(Number(valor ?? 0));

export const fecha = (iso) =>
  new Date(iso).toLocaleString("es-CO", { dateStyle: "medium", timeStyle: "short" });
