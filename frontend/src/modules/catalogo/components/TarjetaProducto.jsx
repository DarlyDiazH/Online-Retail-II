import { BotonAgregar } from "../../carrito";
import { dinero } from "../../carrito/api";

export function TarjetaProducto({ producto, onSeleccionar }) {
  const hayStock = producto.disponible && producto.stock > 0;

  return (
    <article className="tarjeta-producto">
      <div className="tarjeta-imagen-wrap">
        <img
          src={producto.imagen_url}
          alt={producto.nombre}
          className="tarjeta-imagen"
          loading="lazy"
        />
        <span className={`badge-stock ${hayStock ? "en-stock" : "sin-stock"}`}>
          {hayStock ? `Stock: ${producto.stock}` : "Agotado"}
        </span>
      </div>

      <div className="tarjeta-cuerpo">
        <div className="tarjeta-meta">
          <span className="tarjeta-categoria">{producto.categoria}</span>
          <span className="tarjeta-codigo">#{producto.stock_code}</span>
        </div>

        <h3 className="tarjeta-titulo">{producto.nombre}</h3>
        <p className="tarjeta-descripcion">{producto.descripcion}</p>

        <div className="tarjeta-pie">
          <strong className="tarjeta-precio">{dinero(producto.precio)}</strong>
          <button
            type="button"
            className="btn-detalle"
            onClick={() => onSeleccionar(producto.id)}
          >
            Ver detalle
          </button>
        </div>
        <BotonAgregar productoId={producto.id} stock={hayStock ? producto.stock : 0} className="tarjeta-agregar" />
      </div>
    </article>
  );
}