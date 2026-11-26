import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { apiCarrito, fecha } from "../api";
import DetallePedido from "../components/DetallePedido";

export default function ConfirmacionPage() {
  const { codigo } = useParams();
  const { state } = useLocation();
  const [pedido, setPedido] = useState(state?.pedido ?? null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!pedido || pedido.codigo !== codigo) {
      apiCarrito.pedido(codigo).then(setPedido).catch((e) => setError(e.message));
    }
  }, [codigo, pedido]);

  if (error) return <p className="carrito-pagina carrito-error">{error}</p>;
  if (!pedido) return <p className="carrito-pagina">Cargando pedido…</p>;

  return (
    <section className="carrito-pagina carrito-confirmacion">
      {state?.mensaje && <div className="carrito-ok">{state.mensaje}</div>}
      <h1>Pedido {pedido.codigo}</h1>
      <p>
        Estado: <strong>{pedido.estado}</strong> · {fecha(pedido.creado)}
      </p>
      <DetallePedido pedido={pedido} />
      <div className="carrito-acciones">
        <Link className="carrito-btn carrito-btn--primario" to="/catalogo">Seguir comprando</Link>
        <Link className="carrito-btn carrito-btn--texto" to="/mis-pedidos">Ver mis pedidos</Link>
      </div>
    </section>
  );
}
