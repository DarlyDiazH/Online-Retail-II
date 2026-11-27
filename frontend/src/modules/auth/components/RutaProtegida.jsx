import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../AuthContext";

// Úsala como ruta "envoltorio": las rutas hijas solo se ven con sesión iniciada.
//   <Route element={<RutaProtegida />}> ...rutas privadas... </Route>
export default function RutaProtegida() {
  const { autenticado } = useAuth();
  const ubicacion = useLocation();
  if (!autenticado) return <Navigate to="/login" replace state={{ desde: ubicacion.pathname }} />;
  return <Outlet />;
}
