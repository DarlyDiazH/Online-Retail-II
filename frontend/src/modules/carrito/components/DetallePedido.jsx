import { dinero } from "../api";

export default function DetallePedido({ pedido }) {
  return (
    <div className="carrito-detalle">
      <table>
        <thead>
          <tr>
            <th>Producto</th>
            <th>Cant.</th>
            <th>Precio</th>
            <th>Importe</th>
          </tr>
        </thead>
        <tbody>
          {pedido.items.map((i) => (
            <tr key={i.producto_id}>
              <td>{i.nombre}</td>
              <td>{i.cantidad}</td>
              <td>{dinero(i.precio_unitario)}</td>
              <td>{dinero(i.importe)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <dl className="carrito-resumen__filas">
        <dt>Subtotal</dt>
        <dd>{dinero(pedido.subtotal)}</dd>
        {pedido.descuento > 0 && (
          <>
            <dt>Descuento {pedido.segmento} ({pedido.porcentaje_descuento}%)</dt>
            <dd className="carrito-descuento">−{dinero(pedido.descuento)}</dd>
          </>
        )}
        <dt className="carrito-resumen__total">Total</dt>
        <dd className="carrito-resumen__total">{dinero(pedido.total)}</dd>
      </dl>
    </div>
  );
}
