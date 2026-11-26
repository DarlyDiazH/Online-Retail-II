export function FiltrosCatalogo({
  busqueda,
  onBusquedaChange,
  categoria,
  onCategoriaChange,
  categorias,
  soloDisponibles,
  onSoloDisponiblesChange,
  onLimpiar,
  totalResultados,
}) {
  return (
    <section className="catalogo-filtros" aria-label="Filtros del catálogo">
      <div className="filtros-fila">
        <div className="filtro-grupo filtro-busqueda">
          <label htmlFor="input-busqueda">Buscar producto</label>
          <input
            id="input-busqueda"
            type="text"
            placeholder="Nombre, descripción o código (ej. 85123A)..."
            value={busqueda}
            onChange={(e) => onBusquedaChange(e.target.value)}
          />
        </div>

        <div className="filtro-grupo">
          <label htmlFor="select-categoria">Categoría</label>
          <select
            id="select-categoria"
            value={categoria}
            onChange={(e) => onCategoriaChange(e.target.value)}
          >
            <option value="Todas">Todas las categorías</option>
            {categorias.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        <div className="filtro-grupo filtro-check">
          <label htmlFor="check-disponibles" className="checkbox-label">
            <input
              id="check-disponibles"
              type="checkbox"
              checked={soloDisponibles}
              onChange={(e) => onSoloDisponiblesChange(e.target.checked)}
            />
            <span>Solo disponibles</span>
          </label>
        </div>

        <button type="button" className="btn-limpiar" onClick={onLimpiar}>
          Limpiar
        </button>
      </div>

      <div className="filtros-resumen">
        <span>
          {totalResultados} {totalResultados === 1 ? "producto encontrado" : "productos encontrados"}
        </span>
      </div>
    </section>
  );
}