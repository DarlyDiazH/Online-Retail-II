// Cliente HTTP del módulo de autenticación.
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ErrorAuth extends Error {
  constructor(estado, mensaje, campo) {
    super(mensaje);
    this.estado = estado;
    this.campo = campo ?? null;
  }
}

async function pedir(ruta, { method = "GET", body, usuarioId } = {}) {
  let resp;
  try {
    resp = await fetch(`${API_URL}${ruta}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(usuarioId ? { "X-Usuario-Id": String(usuarioId) } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ErrorAuth(0, "No se pudo conectar con el servidor.");
  }
  const datos = await resp.json().catch(() => null);
  if (!resp.ok) {
    const d = datos?.detail;
    if (d && typeof d === "object" && !Array.isArray(d)) throw new ErrorAuth(resp.status, d.mensaje, d.campo);
    if (Array.isArray(d)) {
      // Error de validación del servidor: se muestra el primer mensaje
      const msg = d[0]?.msg?.replace(/^Value error, /, "") ?? "Datos inválidos.";
      throw new ErrorAuth(resp.status, msg);
    }
    throw new ErrorAuth(resp.status, typeof d === "string" ? d : "Ocurrió un error.");
  }
  return datos;
}

export const apiAuth = {
  registro: (datos) => pedir("/api/auth/registro", { method: "POST", body: datos }),
  login: (correo, contrasena) => pedir("/api/auth/login", { method: "POST", body: { correo, contrasena } }),
  perfil: (usuarioId) => pedir("/api/auth/perfil", { usuarioId }),
};
