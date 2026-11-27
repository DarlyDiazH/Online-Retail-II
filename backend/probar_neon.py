"""Revisa la conexión con Neon (solo lee, no cambia nada).

Ejecutar desde backend/:  python probar_neon.py
"""
from sqlalchemy import text

from app.database import engine
from app.modules.carrito.descuentos import BENEFICIOS

if engine.dialect.name != "postgresql":
    raise SystemExit("No estás conectada a Neon: revisa DATABASE_URL en el archivo backend/.env")

with engine.connect() as c:
    filas = c.execute(text(
        "SELECT segmento, descuento_pct, compra_minima_gbp, count(*) "
        "FROM vw_descuentos_checkout GROUP BY 1, 2, 3 ORDER BY 1"
    )).all()
    print("Conexión con Neon: OK\n")
    for segmento, pct, minimo, clientes in filas:
        b = BENEFICIOS.get(segmento)
        igual = b is not None and float(b["porcentaje"]) == float(pct or 0) \
            and float(b["compra_minima"]) == float(minimo or 0)
        print(f"{segmento}: {clientes} clientes, {pct}% desde £{minimo or 0} -> "
              f"{'coincide con el código' if igual else 'REVISAR: no coincide con el código'}")

    ejemplos = c.execute(text(
        "SELECT DISTINCT ON (segmento) segmento, customer_id FROM vw_descuentos_checkout "
        "ORDER BY segmento, customer_id"
    )).all()
    print("\nIDs de cliente para probar el registro:")
    for segmento, cliente in ejemplos:
        print(f"  {cliente} -> {segmento}")

    columnas = c.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = 'usuarios' AND table_schema = current_schema()"
    )).scalars().all()
    if not columnas:
        print("\nTabla usuarios: todavía no existe (se crea al encender el backend).")
    elif {"id", "nombre", "correo", "password_hash", "customer_id", "creado"} <= set(columnas):
        print("\nTabla usuarios: OK")
    else:
        print("\nREVISAR: ya existe una tabla usuarios con otras columnas:", columnas)
