import { Link, useNavigate } from "react-router-dom";
import { dinero, obtenerUsuarioId } from "../api";
import { useCarrito } from "../CarritoContext";
import ResumenCompra from "../components/ResumenCompra";

function LineaCarrito({ item, ocupado, onCantidad, onEliminar }) {
  const maximo = item.stock ?? 999;
  return (
    <li className={`carrito-linea ${!item.disponible ? "tiene-problema" : ""}`}>
      <div className="carrito-linea__img">
        {item.imagen ? <img src={item.imagen} alt={item.nombre} /> : <span>📦</span>}
      </div>

      <div className="carrito-linea__info">
        <h3>{item.nombre}</h3>
        <p className="carrito-linea__precio">{dinero(item.precio_unitario)} c/u</p>
        {item.precio_cambiado && (
          <p className="carrito-alerta">Precio actualizado: {dinero(item.precio_actual)}</p>
        )}
        {!item.disponible && (
          <p className="carrito-alerta">
            {item.stock > 0 ? `Solo quedan ${item.stock} unidades` : "Producto no disponible"}
          </p>
        )}
      </div>

      <div className="carrito-cantidad" role="group" aria-label="Cantidad">
        <button onClick={() => onCantidad(item.cantidad - 1)} disabled={ocupado} aria-label="Restar uno">−</button>
        <input
          type="number"
          min="1"
          max={maximo}
          value={item.cantidad}
          disabled={ocupado}
          onChange={(e) => {
            const n = parseInt(e.target.value, 10);
            if (n >= 1) onCantidad(Math.min(n, maximo));
          }}
        />
        <button
          onClick={() => onCantidad(item.cantidad + 1)}
          disabled={ocupado || item.cantidad >= maximo}
          aria-label="Sumar uno"
        >
          +
        </button>
      </div>

      <p className="carrito-linea__importe">{dinero(item.importe)}</p>

      <button className="carrito-btn carrito-btn--texto" onClick={onEliminar} disabled={ocupado}>
        Eliminar
      </button>
    </li>
  );
}

export default function CarritoPage() {
  const { carrito, cargando, ocupado, error, aviso, cambiarCantidad, eliminar, vaciar, confirmar, limpiarMensajes } =
    useCarrito();
  const navegar = useNavigate();

  if (!obtenerUsuarioId()) {
    return (
      <section className="carrito-pagina carrito-vacio">
        <h1>Tu carrito</h1>
        <p>Inicia sesión para ver tu carrito y tus beneficios.</p>
        <Link className="carrito-btn carrito-btn--primario" to="/login">Iniciar sesión</Link>
      </section>
    );
  }
  if (cargando && !carrito) return <p className="carrito-pagina">Cargando carrito…</p>;
  if (!carrito) return <p className="carrito-pagina carrito-error">{error ?? "No se pudo cargar el carrito."}</p>;

  const alConfirmar = async () => {
    const confirmacion = await confirmar();
    if (confirmacion) navegar(`/pedido/${confirmacion.pedido.codigo}`, { state: confirmacion });
  };

  const hayProblemas = carrito.items.some((i) => !i.disponible);

  return (
    <section className="carrito-pagina">
      <h1>Tu carrito</h1>

      {error && (
        <div className="carrito-error" role="alert">
          {error} <button onClick={limpiarMensajes} aria-label="Cerrar">×</button>
        </div>
      )}
      {aviso && !error && (
        <div className="carrito-ok" role="status">
          {aviso} <button onClick={limpiarMensajes} aria-label="Cerrar">×</button>
        </div>
      )}
      {carrito.avisos?.length > 0 && (
        <ul className="carrito-avisos">
          {carrito.avisos.map((a) => <li key={a}>{a}</li>)}
        </ul>
      )}

      {carrito.items.length === 0 ? (
        <div className="carrito-vacio">
          <p>Tu carrito está vacío.</p>
          <Link className="carrito-btn carrito-btn--primario" to="/catalogo">Ver productos</Link>
          <Link className="carrito-btn carrito-btn--texto" to="/mis-pedidos">Ver mis pedidos</Link>
        </div>
      ) : (
        <div className="carrito-grid">
          <div>
            <ul className="carrito-lista">
              {carrito.items.map((item) => (
                <LineaCarrito
                  key={item.producto_id}
                  item={item}
                  ocupado={ocupado}
                  onCantidad={(n) => cambiarCantidad(item.producto_id, n)}
                  onEliminar={() => eliminar(item.producto_id)}
                />
              ))}
            </ul>
            <div className="carrito-acciones">
              <Link to="/catalogo">← Seguir comprando</Link>
              <button
                className="carrito-btn carrito-btn--texto"
                disabled={ocupado}
                onClick={() => window.confirm("¿Vaciar el carrito?") && vaciar()}
              >
                Vaciar carrito
              </button>
            </div>
          </div>
          <ResumenCompra carrito={carrito} onConfirmar={alConfirmar} ocupado={ocupado} hayProblemas={hayProblemas} />
        </div>
      )}
    </section>
  );
}
