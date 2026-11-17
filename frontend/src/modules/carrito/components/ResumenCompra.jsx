import { dinero } from "../api";

// Resumen de compra con el beneficio del segmento del cliente.
export default function ResumenCompra({ carrito, onConfirmar, ocupado, hayProblemas }) {
  const { subtotal, descuento, total, cantidad_articulos, beneficio } = carrito;

  return (
    <aside className="carrito-resumen">
      <h2>Resumen de compra</h2>

      <div className={`carrito-beneficio ${beneficio.aplicado ? "es-activo" : ""}`}>
        <span className="carrito-beneficio__segmento">Cliente {beneficio.segmento}</span>
        <p>{beneficio.descripcion}</p>
        {!beneficio.aplicado && beneficio.falta_para_aplicar > 0 && (
          <p className="carrito-beneficio__falta">
            Te faltan {dinero(beneficio.falta_para_aplicar)} para activar tu descuento.
          </p>
        )}
      </div>

      <dl className="carrito-resumen__filas">
        <dt>Artículos</dt>
        <dd>{cantidad_articulos}</dd>
        <dt>Subtotal</dt>
        <dd>{dinero(subtotal)}</dd>
        {descuento > 0 && (
          <>
            <dt>Descuento ({beneficio.porcentaje}%)</dt>
            <dd className="carrito-descuento">−{dinero(descuento)}</dd>
          </>
        )}
        <dt className="carrito-resumen__total">Total</dt>
        <dd className="carrito-resumen__total">{dinero(total)}</dd>
      </dl>

      {descuento > 0 && <p className="carrito-ahorro">Ahorras {dinero(descuento)} en esta compra 🎉</p>}

      <button
        className="carrito-btn carrito-btn--primario carrito-btn--ancho"
        onClick={onConfirmar}
        disabled={ocupado || hayProblemas || cantidad_articulos === 0}
      >
        {ocupado ? "Procesando…" : "Confirmar pedido"}
      </button>
      <p className="carrito-nota">Compra simulada: no se realizará ningún cobro.</p>
    </aside>
  );
}
