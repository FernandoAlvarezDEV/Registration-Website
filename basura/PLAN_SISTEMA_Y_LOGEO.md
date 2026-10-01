# 📋 Especificación del Sistema Onda Fest 2026

> **IMPORTANTE PARA DESARROLLADORES Y MODELOS DE IA:**
> - **CERO CORREOS ELECTRÓNICOS:** No se envía ningún correo automático por SMTP/Resend.
> - **CERO MAGIC LINKS:** No existen enlaces mágicos de autenticación por URL.
> - **ACCESO POR VALIDACIÓN DE DATOS:** Los usuarios normales acceden a su panel validando sus datos (Nombre, Teléfono, Municipio/Distrito, Correo).
> - **SOPORTE TÉCNICO OFICIAL:** WhatsApp **829-753-4583**.

---

## 1. 🎟️ Generación y Formato del Código de Registro (ENO-A001 a ENO-Z100)

El código de registro es secuencial y tiene un tope máximo de 2,600 asistentes (26 letras del alfabeto × 100 registros por letra):
- Registros 1 a 100: **ENO-A001** a **ENO-A100**
- Registros 101 a 200: **ENO-B001** a **ENO-B100**
- Registros 201 a 300: **ENO-C001** a **ENO-C100**
- ...
- Registros 2501 a 2600: **ENO-Z001** a **ENO-Z100**

### Fórmula de asignación:
Dado un índice secuencial `idx` (iniciando en 0):
- `letra_idx = idx // 100` (0 = A, 1 = B, ..., 25 = Z)
- `numero = (idx % 100) + 1` (de 1 a 100)
- `codigo = f"ENO-{chr(65 + letra_idx)}{numero:03d}"`

---

## 2. 🌊 Flujo del Usuario Participante

```
[ Formulario de Registro ]  (frontend/inscripcion.html)
        │
        ▼ (Envía datos a POST /api/registros)
[ Confirmación de Registro ] (frontend/success.html)
   • Muestra su código (ej: ENO-A001)
   • Datos bancarios (Popular, Hamlet, RD$600)
   • Instrucción: Poner en la transferencia: "ENO-A001 - Nombre - Municipio/Distrito"
   • Botón directo: "Revisar mi inscripción / Subir comprobante"
        │
        ▼
[ Pantalla de Acceso Usuario ] (frontend/dashboard.html)
   • Solicita 4 datos para validar identidad:
     1. Nombre Completo
     2. Teléfono
     3. Municipio / Distrito
     4. Correo Electrónico
        │
        ▼ (Valida contra POST /api/registros/acceso)
[ Panel de Usuario Asistente ] (frontend/dashboard.html)
   • Consulta estado del registro y estado del pago (Pendiente / En revisión / Verificado)
   • Subida de foto del comprobante de pago
   • Datos de la cuenta bancaria para pagar
   • Botón de ayuda técnica WhatsApp: 829-753-4583
```

---

## 3. 💳 Datos de Pago Oficiales
- **Banco:** Banco Popular Dominicano
- **Titular:** Hamlet
- **No. de Cuenta:** 123-456789-0 (Corriente)
- **Cédula:** 001-1234567-8
- **Monto:** RD$600.00
- **Concepto obligatorio:** `[CÓDIGO] - [Nombre Completo] - [Distrito/Municipio]`
  *(Ejemplo: ENO-A001 - Juan Pérez - Distrito Nacional)*

---

## 4. 🛠️ Endpoints del Backend
- `POST /api/registros`: Crea el registro, calcula y asigna el código `ENO-X###`. **NO** dispara emails.
- `POST /api/registros/verificar`: Recibe `{ nombre, telefono, distrito, email }`. Valida los datos y devuelve el registro del usuario con su estado actual y datos para el panel.
- `POST /api/registros/{id}/comprobante`: Recibe la imagen del comprobante de pago y actualiza el estado a `en revisión`.
- `POST /api/auth/admin`: Acceso exclusivo para administradores.
