import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiCarrito, dinero, fecha } from "../api";
import DetallePedido from "../components/DetallePedido";

export default function HistorialPage() {
  const [pedidos, setPedidos] = useState(null);
  const [error, setError] = useState(null);
  const [abierto, setAbierto] = useState(null); // código del pedido desplegado
  const [detalles, setDetalles] = useState({});

  useEffect(() => {
    apiCarrito.historial().then(setPedidos).catch((e) => setError(e.message));
  }, []);

  const alternar = async (codigo) => {
    if (abierto === codigo) return setAbierto(null);
    setAbierto(codigo);
    if (!detalles[codigo]) {
      try {
        const d = await apiCarrito.pedido(codigo);
        setDetalles((prev) => ({ ...prev, [codigo]: d }));
      } catch (e) {
        setError(e.message);
      }
    }
  };

  if (error) return <p className="carrito-pagina carrito-error">{error}</p>;
  if (!pedidos) return <p className="carrito-pagina">Cargando pedidos…</p>;

  return (
    <section className="carrito-pagina">
      <h1>Mis pedidos</h1>
      {pedidos.length === 0 ? (
        <div className="carrito-vacio">
          <p>Aún no tienes pedidos.</p>
          <Link className="carrito-btn carrito-btn--primario" to="/catalogo">Ir al catálogo</Link>
        </div>
      ) : (
        <ul className="carrito-historial">
          {pedidos.map((p) => (
            <li key={p.codigo}>
              <button className="carrito-historial__fila" onClick={() => alternar(p.codigo)} aria-expanded={abierto === p.codigo}>
                <span className="carrito-historial__codigo">{p.codigo}</span>
                <span>{fecha(p.creado)}</span>
                <span>{p.cantidad_articulos} art.</span>
                <span className="carrito-historial__estado">{p.estado}</span>
                <strong>{dinero(p.total)}</strong>
              </button>
              {abierto === p.codigo &&
                (detalles[p.codigo] ? <DetallePedido pedido={detalles[p.codigo]} /> : <p>Cargando…</p>)}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
