const BASE_URL =
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_URL) ||
  "http://127.0.0.1:8000";

const CATALOGO_URL = `${BASE_URL}/catalogo`;

export async function obtenerProductos({ busqueda = "", categoria = "Todas", soloDisponibles = false } = {}) {
  const params = new URLSearchParams();

  if (busqueda.trim()) {
    params.set("busqueda", busqueda.trim());
  }
  if (categoria && categoria !== "Todas") {
    params.set("categoria", categoria);
  }
  if (soloDisponibles) {
    params.set("solo_disponibles", "true");
  }

  const queryString = params.toString();
  const url = queryString ? `${CATALOGO_URL}/productos?${queryString}` : `${CATALOGO_URL}/productos`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("No se pudieron cargar los productos del catálogo");
  }
  return response.json();
}

export async function obtenerCategorias() {
  const response = await fetch(`${CATALOGO_URL}/categorias`);
  if (!response.ok) {
    throw new Error("No se pudieron cargar las categorías");
  }
  return response.json();
}

export async function obtenerDetalleProducto(productoId) {
  const response = await fetch(`${CATALOGO_URL}/productos/${encodeURIComponent(productoId)}`);
  if (!response.ok) {
    throw new Error("No se encontró el detalle del producto");
  }
  return response.json();
}

export async function consultarDisponibilidadProducto(productoId, cantidad = 1) {
  const params = new URLSearchParams({ cantidad: String(cantidad) });
  const response = await fetch(
    `${CATALOGO_URL}/productos/${encodeURIComponent(productoId)}/disponibilidad?${params.toString()}`
  );
  if (!response.ok) {
    throw new Error("No se pudo verificar la disponibilidad");
  }
  return response.json();
}