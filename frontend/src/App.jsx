// Ensambla los módulos. Si alguien más ya creó App.jsx, solo hay que sumar lo que falte.
// Orden de los proveedores: CarritoProvider por fuera, AuthProvider por dentro.
import { BrowserRouter, Link, Navigate, Route, Routes } from "react-router-dom";
import { CarritoProvider, IconoCarrito, rutasCarrito } from "./modules/carrito";
import { AuthProvider, MenuUsuario, RutaProtegida, rutasAuthPrivadas, rutasAuthPublicas } from "./modules/auth";
import { CatalogoPage } from "./modules/catalogo";

export default function App() {
  return (
    <BrowserRouter>
      <CarritoProvider>
        <AuthProvider>
          <nav className="barra">
            <Link to="/catalogo" className="barra__marca">Online Retail II</Link>
            <span className="barra__der">
              <IconoCarrito />
              <MenuUsuario />
            </span>
          </nav>

          <Routes>
            <Route path="/" element={<Navigate to="/catalogo" replace />} />
            <Route path="/catalogo" element={<CatalogoPage />} />
            {rutasAuthPublicas}

            {/* Rutas que exigen iniciar sesión */}
            <Route element={<RutaProtegida />}>
              {rutasAuthPrivadas}
              {rutasCarrito}
            </Route>
          </Routes>
        </AuthProvider>
      </CarritoProvider>
    </BrowserRouter>
  );
}