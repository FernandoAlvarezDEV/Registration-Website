from database import engine
from sqlalchemy import text

conn = engine.connect()
try:
    conn.execute(text("ALTER TABLE registros ADD COLUMN comprobante_pago VARCHAR(512) DEFAULT NULL"))
    print("Added comprobante_pago column")
except Exception as e:
    print(f"comprobante_pago: {e}")

try:
    conn.execute(text("ALTER TABLE registros ADD COLUMN estado_pago VARCHAR(20) NOT NULL DEFAULT 'pendiente'"))
    print("Added estado_pago column")
except Exception as e:
    print(f"estado_pago: {e}")

conn.commit()
conn.close()
print("Done!")
