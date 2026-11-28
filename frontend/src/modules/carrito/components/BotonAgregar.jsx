import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { obtenerUsuarioId } from "../api";
import { useCarrito } from "../CarritoContext";

// Para usar en las tarjetas y el detalle del catálogo (Persona 2):
//   <BotonAgregar productoId={producto.id} stock={producto.stock} />
export default function BotonAgregar({ productoId, stock, cantidad = 1, texto = "Agregar al carrito", className = "" }) {
  const { agregar, ocupado, error, limpiarMensajes } = useCarrito();
  const navegar = useNavigate();
  const [estado, setEstado] = useState(null); // null | "ok" | "error"
  const agotado = stock !== undefined && stock !== null && stock <= 0;

  const alHacerClic = async (e) => {
    e.stopPropagation();
    if (!obtenerUsuarioId()) {
      navegar("/login");
      return;
    }
    limpiarMensajes();
    const ok = await agregar(productoId, cantidad);
    setEstado(ok ? "ok" : "error");
    if (ok) setTimeout(() => setEstado(null), 1500);
  };

  return (
    <span className={`carrito-agregar ${className}`}>
      <button
        type="button"
        className="carrito-btn carrito-btn--primario"
        onClick={alHacerClic}
        disabled={ocupado || agotado}
      >
        {agotado ? "Agotado" : estado === "ok" ? "✓ Agregado" : texto}
      </button>
      {estado === "error" && error && <small className="carrito-agregar__error">{error}</small>}
    </span>
  );
}
