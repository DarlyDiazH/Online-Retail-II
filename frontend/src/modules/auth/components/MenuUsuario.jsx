import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

// Para la barra de navegación: saludo y salir, o enlaces de entrar y registrarse.
export default function MenuUsuario() {
  const { usuario, autenticado, logout } = useAuth();
  const navegar = useNavigate();

  if (!autenticado) {
    return (
      <span className="auth-menu">
        <Link to="/login">Iniciar sesión</Link>
        <Link to="/registro" className="auth-menu__boton">Registrarse</Link>
      </span>
    );
  }
  return (
    <span className="auth-menu">
      <Link to="/perfil">Hola, {usuario.nombre.split(" ")[0]}</Link>
      <Link to="/mis-pedidos">Mis pedidos</Link>
      <button
        type="button"
        className="auth-menu__salir"
        onClick={() => {
          logout();
          navegar("/login");
        }}
      >
        Cerrar sesión
      </button>
    </span>
  );
}
