import { useEffect, useState } from "react";
import { consultarDisponibilidadProducto } from "../api";

export function DetalleProducto({ producto, onCerrar }) {
  const [cantidad, setCantidad] = useState(1);
  const [consultaStock, setConsultaStock] = useState(null);
  const [consultando, setConsultando] = useState(false);

  useEffect(() => {
    setCantidad(1);
    setConsultaStock(null);
  }, [producto]);

  if (!producto) {
    return null;
  }

  const hayStock = producto.disponible && producto.stock > 0;

  async function handleVerificarCantidad(e) {
    e.preventDefault();
    setConsultando(true);
    try {
      const resultado = await consultarDisponibilidadProducto(producto.id, Number(cantidad));
      setConsultaStock(resultado);
    } catch {
      setConsultaStock({ error: "No se pudo verificar la cantidad." });
    } finally {
      setConsultando(false);
    }
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="detalle-titulo">
      <div className="modal-contenido">
        <button
          type="button"
          className="modal-cerrar"
          onClick={onCerrar}
          aria-label="Cerrar detalle"
        >
          ✕
        </button>

        <div className="detalle-grid">
          <img
            src={producto.imagen_url}
            alt={producto.nombre}
            className="detalle-imagen"
          />

          <div className="detalle-info">
            <span className="tarjeta-categoria">{producto.categoria}</span>
            <h2 id="detalle-titulo">{producto.nombre}</h2>
            <p className="detalle-codigos">
              ID: <strong>{producto.id}</strong> · Código: <strong>{producto.stock_code}</strong>
            </p>
            <p className="detalle-descripcion">{producto.descripcion}</p>
            <p className="detalle-precio">${producto.precio.toFixed(2)}</p>
            <p className={`estado-texto ${hayStock ? "en-stock" : "sin-stock"}`}>
              {hayStock
                ? `Disponible (${producto.stock} unidades en inventario)`
                : "Sin stock disponible actualmente"}
            </p>

            <form className="form-disponibilidad" onSubmit={handleVerificarCantidad}>
              <label htmlFor="input-cantidad">Consultar cantidad:</label>
              <div className="disponibilidad-controles">
                <input
                  id="input-cantidad"
                  type="number"
                  min={1}
                  value={cantidad}
                  onChange={(e) => setCantidad(e.target.value)}
                />
                <button type="submit" disabled={consultando}>
                  {consultando ? "Verificando..." : "Verificar stock"}
                </button>
              </div>
            </form>

            {consultaStock && !consultaStock.error && (
              <p className="resultado-disponibilidad">
                {consultaStock.disponible_para_cantidad
                  ? `Sí hay ${consultaStock.cantidad_solicitada} unidad(es) disponibles.`
                  : `No hay ${consultaStock.cantidad_solicitada} unidad(es) disponibles (máx. ${consultaStock.stock_disponible}).`}
              </p>
            )}

            {consultaStock?.error && (
              <p className="error-texto">{consultaStock.error}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}