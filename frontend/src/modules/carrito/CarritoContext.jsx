import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { apiCarrito, obtenerUsuarioId } from "./api";

const CarritoContext = createContext(null);

// Envuelve la app con <CarritoProvider> para que cualquier pantalla (catálogo,
// detalle de producto, navbar) pueda usar useCarrito().
export function CarritoProvider({ children }) {
  const [carrito, setCarrito] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState(null);
  const [aviso, setAviso] = useState(null);

  const cargar = useCallback(async () => {
    if (!obtenerUsuarioId()) {
      setCarrito(null);
      return;
    }
    setCargando(true);
    setError(null);
    try {
      setCarrito(await apiCarrito.ver());
    } catch (e) {
      setError(e.message);
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    cargar();
  }, [cargar]);

  // Ejecuta una acción que devuelve el carrito actualizado
  const ejecutar = useCallback(async (accion, mensajeOk) => {
    setOcupado(true);
    setError(null);
    try {
      const nuevo = await accion();
      setCarrito(nuevo);
      if (mensajeOk) setAviso(mensajeOk);
      return true;
    } catch (e) {
      if (e.detalle?.carrito) setCarrito(e.detalle.carrito);
      setError(e.message);
      return false;
    } finally {
      setOcupado(false);
    }
  }, []);

  const confirmar = useCallback(async () => {
    setOcupado(true);
    setError(null);
    try {
      const confirmacion = await apiCarrito.confirmar(carrito?.total);
      await cargar();
      return confirmacion;
    } catch (e) {
      if (e.detalle?.carrito) setCarrito(e.detalle.carrito);
      const problemas = e.detalle?.problemas?.join(" ");
      setError(problemas ? `${e.message} ${problemas}` : e.message);
      return null;
    } finally {
      setOcupado(false);
    }
  }, [carrito?.total, cargar]);

  const valor = useMemo(
    () => ({
      carrito,
      cantidad: carrito?.cantidad_articulos ?? 0,
      cargando,
      ocupado,
      error,
      aviso,
      limpiarMensajes: () => {
        setError(null);
        setAviso(null);
      },
      cargar,
      agregar: (id, cant = 1) => ejecutar(() => apiCarrito.agregar(id, cant), "Producto agregado al carrito."),
      cambiarCantidad: (id, cant) => ejecutar(() => apiCarrito.cambiarCantidad(id, cant)),
      eliminar: (id) => ejecutar(() => apiCarrito.eliminar(id), "Producto eliminado."),
      vaciar: () => ejecutar(() => apiCarrito.vaciar(), "Carrito vaciado."),
      confirmar,
    }),
    [carrito, cargando, ocupado, error, aviso, cargar, ejecutar, confirmar]
  );

  return <CarritoContext.Provider value={valor}>{children}</CarritoContext.Provider>;
}

export function useCarrito() {
  const ctx = useContext(CarritoContext);
  if (!ctx) throw new Error("useCarrito debe usarse dentro de <CarritoProvider>");
  return ctx;
}
