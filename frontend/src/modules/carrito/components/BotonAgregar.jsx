import { useState } from "react";
import { useCarrito } from "../CarritoContext";

// Para usar en las tarjetas y el detalle del catálogo (Persona 2):
//   <BotonAgregar productoId={producto.id} stock={producto.stock} />
export default function BotonAgregar({ productoId, stock, cantidad = 1, texto = "Agregar al carrito" }) {
  const { agregar, ocupado } = useCarrito();
  const [listo, setListo] = useState(false);
  const agotado = stock !== undefined && stock !== null && stock <= 0;

  const alHacerClic = async () => {
    if (await agregar(productoId, cantidad)) {
      setListo(true);
      setTimeout(() => setListo(false), 1500);
    }
  };

  return (
    <button className="carrito-btn carrito-btn--primario" onClick={alHacerClic} disabled={ocupado || agotado}>
      {agotado ? "Agotado" : listo ? "✓ Agregado" : texto}
    </button>
  );
}
