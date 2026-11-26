import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { apiAuth } from "./api";
import { useCarrito } from "../carrito";

// Importante: <AuthProvider> debe ir DENTRO de <CarritoProvider> (ver App.jsx),
// porque al entrar o salir hay que recargar el carrito.
const AuthContext = createContext(null);

const CLAVE_ID = "usuario_id"; // la misma que lee el módulo de carrito
const CLAVE_PERFIL = "usuario_perfil";

function leerPerfilGuardado() {
  try {
    return JSON.parse(localStorage.getItem(CLAVE_PERFIL));
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const { cargar: recargarCarrito } = useCarrito();
  const [usuario, setUsuario] = useState(() =>
    localStorage.getItem(CLAVE_ID) ? leerPerfilGuardado() : null
  );

  const guardarSesion = useCallback(
    (perfil) => {
      localStorage.setItem(CLAVE_ID, String(perfil.id));
      localStorage.setItem(CLAVE_PERFIL, JSON.stringify(perfil));
      setUsuario(perfil);
      recargarCarrito();
    },
    [recargarCarrito]
  );

  const login = useCallback(
    async (correo, contrasena) => guardarSesion(await apiAuth.login(correo, contrasena)),
    [guardarSesion]
  );

  const registrar = useCallback(
    async (datos) => guardarSesion(await apiAuth.registro(datos)),
    [guardarSesion]
  );

  const logout = useCallback(() => {
    localStorage.removeItem(CLAVE_ID);
    localStorage.removeItem(CLAVE_PERFIL);
    setUsuario(null);
    recargarCarrito(); // sin usuario_id, el carrito se vacía de la pantalla
  }, [recargarCarrito]);

  // Al abrir la app, refresca el perfil (por si cambió el segmento). Si el usuario ya no existe, cierra sesión.
  useEffect(() => {
    const id = localStorage.getItem(CLAVE_ID);
    if (!id) return;
    apiAuth
      .perfil(id)
      .then((perfil) => {
        localStorage.setItem(CLAVE_PERFIL, JSON.stringify(perfil));
        setUsuario(perfil);
      })
      .catch((e) => {
        if (e.estado === 401) logout();
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const valor = useMemo(
    () => ({ usuario, autenticado: !!usuario, login, registrar, logout }),
    [usuario, login, registrar, logout]
  );
  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}
