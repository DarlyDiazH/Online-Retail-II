// Punto de entrada del módulo de carrito.
//
// En main.jsx / App.jsx (quien arme la app):
//   import { CarritoProvider, rutasCarrito, IconoCarrito } from "./modules/carrito";
//   <BrowserRouter>
//     <CarritoProvider>
//       <nav>... <IconoCarrito /> </nav>
//       <Routes>
//         {rutasCarrito}
//         ...rutas de los otros módulos
//       </Routes>
//     </CarritoProvider>
//   </BrowserRouter>
import { Route } from "react-router-dom";
import "./carrito.css";
import CarritoPage from "./pages/CarritoPage";
import ConfirmacionPage from "./pages/ConfirmacionPage";
import HistorialPage from "./pages/HistorialPage";

export { CarritoProvider, useCarrito } from "./CarritoContext";
export { default as BotonAgregar } from "./components/BotonAgregar";
export { default as IconoCarrito } from "./components/IconoCarrito";
export { CarritoPage, ConfirmacionPage, HistorialPage };

export const rutasCarrito = [
  <Route key="carrito" path="/carrito" element={<CarritoPage />} />,
  <Route key="pedido" path="/pedido/:codigo" element={<ConfirmacionPage />} />,
  <Route key="mis-pedidos" path="/mis-pedidos" element={<HistorialPage />} />,
];
