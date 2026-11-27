// Punto de entrada del módulo de autenticación y perfil.
//   import { AuthProvider, rutasAuth, RutaProtegida, MenuUsuario } from "./modules/auth";
import { Route } from "react-router-dom";
import "./auth.css";
import LoginPage from "./pages/LoginPage";
import RegistroPage from "./pages/RegistroPage";
import PerfilPage from "./pages/PerfilPage";

export { AuthProvider, useAuth } from "./AuthContext";
export { default as RutaProtegida } from "./components/RutaProtegida";
export { default as MenuUsuario } from "./components/MenuUsuario";
export { LoginPage, RegistroPage, PerfilPage };

// Rutas públicas (login y registro)
export const rutasAuthPublicas = [
  <Route key="login" path="/login" element={<LoginPage />} />,
  <Route key="registro" path="/registro" element={<RegistroPage />} />,
];

// Rutas que exigen sesión (perfil)
export const rutasAuthPrivadas = [
  <Route key="perfil" path="/perfil" element={<PerfilPage />} />,
];
