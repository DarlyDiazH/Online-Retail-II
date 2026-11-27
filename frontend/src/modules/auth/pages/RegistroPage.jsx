import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

const CORREO = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

export default function RegistroPage() {
  const { registrar, autenticado } = useAuth();
  const navegar = useNavigate();
  const [f, setF] = useState({ nombre: "", correo: "", contrasena: "", confirmar: "", customerId: "" });
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState(null);
  const [enviando, setEnviando] = useState(false);

  if (autenticado) return <Navigate to="/catalogo" replace />;

  const cambiar = (campo) => (e) => setF({ ...f, [campo]: e.target.value });

  function validar() {
    const e = {};
    if (f.nombre.trim().length < 2) e.nombre = "Escribe tu nombre.";
    if (!CORREO.test(f.correo.trim())) e.correo = "Escribe un correo válido.";
    if (f.contrasena.length < 8) e.contrasena = "Mínimo 8 caracteres.";
    if (f.confirmar !== f.contrasena) e.confirmar = "Las contraseñas no coinciden.";
    if (f.customerId.trim() && !/^\d+$/.test(f.customerId.trim())) e.customerId = "El ID de cliente solo tiene números.";
    return e;
  }

  async function enviar(ev) {
    ev.preventDefault();
    setErrorGeneral(null);
    const e = validar();
    setErrores(e);
    if (Object.keys(e).length) return;
    setEnviando(true);
    try {
      await registrar({
        nombre: f.nombre,
        correo: f.correo,
        contrasena: f.contrasena,
        customer_id: f.customerId.trim() ? Number(f.customerId.trim()) : null,
      });
      navegar("/perfil", { replace: true });
    } catch (err) {
      const campo = { correo: "correo", customer_id: "customerId" }[err.campo];
      if (campo) setErrores({ [campo]: err.message });
      else setErrorGeneral(err.message);
    } finally {
      setEnviando(false);
    }
  }

  const campo = (id, etiqueta, tipo = "text", extra = {}) => (
    <label>
      {etiqueta}
      <input type={tipo} value={f[id]} onChange={cambiar(id)} {...extra} />
      {errores[id] && <span className="auth-error" role="alert">{errores[id]}</span>}
    </label>
  );

  return (
    <main className="auth-pagina">
      <form className="auth-tarjeta" onSubmit={enviar} noValidate>
        <h1>Crear cuenta</h1>
        {campo("nombre", "Nombre completo", "text", { autoComplete: "name" })}
        {campo("correo", "Correo", "email", { autoComplete: "email" })}
        {campo("contrasena", "Contraseña", "password", { autoComplete: "new-password" })}
        {campo("confirmar", "Confirmar contraseña", "password", { autoComplete: "new-password" })}
        {campo("customerId", "ID de cliente (opcional)", "text", { inputMode: "numeric", placeholder: "Solo si ya eras cliente" })}
        <p className="auth-ayuda">Si ya compraste antes, escribe tu ID de cliente para recuperar tus beneficios. Si lo dejas vacío, serás cliente nuevo.</p>
        {errorGeneral && <p className="auth-error" role="alert">{errorGeneral}</p>}
        <button type="submit" disabled={enviando}>{enviando ? "Creando cuenta…" : "Registrarme"}</button>
        <p className="auth-pie">¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link></p>
      </form>
    </main>
  );
}
