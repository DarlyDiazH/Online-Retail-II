import { Link } from "react-router-dom";
import { useCarrito } from "../CarritoContext";

// Para la barra de navegación: muestra el carrito con el número de artículos.
export default function IconoCarrito() {
  const { cantidad } = useCarrito();
  return (
    <Link to="/carrito" className="carrito-icono" aria-label={`Carrito, ${cantidad} artículos`}>
      🛒{cantidad > 0 && <span className="carrito-icono__badge">{cantidad}</span>}
    </Link>
  );
}
