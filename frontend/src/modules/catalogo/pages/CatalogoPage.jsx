import { useEffect, useState } from "react";
import {
  obtenerCategorias,
  obtenerDetalleProducto,
  obtenerProductos,
} from "../api";
import { DetalleProducto } from "../components/DetalleProducto";
import { FiltrosCatalogo } from "../components/FiltrosCatalogo";
import { TarjetaProducto } from "../components/TarjetaProducto";
import "../catalogo.css";

export function CatalogoPage() {
  const [productos, setProductos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [categoria, setCategoria] = useState("Todas");
  const [soloDisponibles, setSoloDisponibles] = useState(false);
  const [productoSeleccionado, setProductoSeleccionado] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    obtenerCategorias()
      .then(setCategorias)
      .catch(() => setCategorias([]));
  }, []);

  useEffect(() => {
    let activo = true;
    setCargando(true);
    setError("");

    obtenerProductos({ busqueda, categoria, soloDisponibles })
      .then((data) => {
        if (activo) {
          setProductos(data.productos || []);
        }
      })
      .catch((err) => {
        if (activo) {
          setError(err.message || "Error al cargar el catálogo");
        }
      })
      .finally(() => {
        if (activo) {
          setCargando(false);
        }
      });

    return () => {
      activo = false;
    };
  }, [busqueda, categoria, soloDisponibles]);

  function handleLimpiarFiltros() {
    setBusqueda("");
    setCategoria("Todas");
    setSoloDisponibles(false);
  }

  async function handleSeleccionarProducto(productoId) {
    try {
      const detalle = await obtenerDetalleProducto(productoId);
      setProductoSeleccionado(detalle);
    } catch (err) {
      setError(err.message || "No se pudo abrir el detalle del producto");
    }
  }

  return (
    <main className="catalogo-contenedor">
      <header className="catalogo-header">
        <h1>Catálogo de Productos</h1>
        <p>Online Retail II · Explora, filtra y consulta disponibilidad en tiempo real</p>
      </header>

      <FiltrosCatalogo
        busqueda={busqueda}
        onBusquedaChange={setBusqueda}
        categoria={categoria}
        onCategoriaChange={setCategoria}
        categorias={categorias}
        soloDisponibles={soloDisponibles}
        onSoloDisponiblesChange={setSoloDisponibles}
        onLimpiar={handleLimpiarFiltros}
        totalResultados={productos.length}
      />

      {error && <div className="catalogo-alerta error">{error}</div>}

      {cargando ? (
        <div className="catalogo-estado">Cargando productos...</div>
      ) : productos.length === 0 ? (
        <div className="catalogo-estado">
          No hay productos que coincidan con los filtros seleccionados.
        </div>
      ) : (
        <section className="catalogo-grid" aria-label="Lista de productos">
          {productos.map((producto) => (
            <TarjetaProducto
              key={producto.id}
              producto={producto}
              onSeleccionar={handleSeleccionarProducto}
            />
          ))}
        </section>
      )}

      <DetalleProducto
        producto={productoSeleccionado}
        onCerrar={() => setProductoSeleccionado(null)}
      />
    </main>
  );
}