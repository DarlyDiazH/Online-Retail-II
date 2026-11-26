import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function LoginPage() {
  const { login, autenticado } = useAuth();
  const navegar = useNavigate();
  const ubicacion = useLocation();
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState(null);
  const [enviando, setEnviando] = useState(false);

  if (autenticado) return <Navigate to="/catalogo" replace />;

  async function enviar(e) {
    e.preventDefault();
    setError(null);
    if (!correo.trim() || !contrasena) return setError("Escribe tu correo y tu contraseña.");
    setEnviando(true);
    try {
      await login(correo, contrasena);
      navegar(ubicacion.state?.desde ?? "/catalogo", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="auth-pagina">
      <form className="auth-tarjeta" onSubmit={enviar} noValidate>
        <h1>Iniciar sesión</h1>
        <label>
          Correo
          <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} autoComplete="email" />
        </label>
        <label>
          Contraseña
          <input type="password" value={contrasena} onChange={(e) => setContrasena(e.target.value)} autoComplete="current-password" />
        </label>
        {error && <p className="auth-error" role="alert">{error}</p>}
        <button type="submit" disabled={enviando}>{enviando ? "Entrando…" : "Entrar"}</button>
        <p className="auth-pie">¿No tienes cuenta? <Link to="/registro">Regístrate</Link></p>
      </form>
    </main>
  );
}
