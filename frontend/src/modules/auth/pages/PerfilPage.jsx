import { Link } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function PerfilPage() {
  const { usuario } = useAuth();
  const b = usuario.beneficio;

  return (
    <main className="auth-pagina">
      <section className="auth-tarjeta auth-tarjeta--ancha">
        <h1>Mi perfil</h1>
        <dl className="auth-datos">
          <dt>Nombre</dt><dd>{usuario.nombre}</dd>
          <dt>Correo</dt><dd>{usuario.correo}</dd>
          <dt>ID de cliente</dt>
          <dd>{usuario.customer_id ?? "Sin coincidencia histórica"}</dd>
          <dt>Segmento</dt>
          <dd>
            {usuario.segmento}
            {usuario.es_nuevo && <small> (categoría provisional para clientes nuevos)</small>}
          </dd>
        </dl>

        <div className="auth-beneficio">
          <h2>Tu beneficio</h2>
          <p className="auth-beneficio__pct">{b.porcentaje}% de descuento</p>
          <p>{b.descripcion}</p>
        </div>

        <p className="auth-pie">
          <Link to="/catalogo">Ir al catálogo</Link> · <Link to="/mis-pedidos">Ver mis pedidos</Link>
        </p>
      </section>
    </main>
  );
}
