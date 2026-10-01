# Plan de Mejoras — OndaFest2026 Registro

Feedback recolectado de sesión de prueba con 20 personas (27 sept 2026).

---

## 🔴 Prioridad alta

### 1. Separar "Contacto de Emergencia" en 3 campos
**Estado actual:** un solo campo de texto libre ("Nombre y teléfono") + un campo aparte de "Parentesco".

**Cambio:** dividir en 3 campos independientes dentro de la misma sección:
1. **Nombre del contacto de emergencia** (texto)
2. **Teléfono del contacto de emergencia** (número, mismo formato que el teléfono del registrado: `809-555-1234`)
3. **Parentesco** (ya existe, se mantiene — ej: Madre, Padre, Hermano/a)

**Impacto en backend:** el modelo `Registro` probablemente tiene un solo campo `contacto_emergencia` (texto libre). Hay que:
- Agregar columna nueva `contacto_emergencia_telefono` (String)
- Renombrar o mantener `contacto_emergencia` solo para el nombre
- `parentesco` ya existe, no se toca
- Si ya hay registros en producción con el campo viejo combinado, evaluar si se migra data existente o se deja como está (dado el volumen bajo, probablemente no amerita migración de data, solo el cambio de esquema hacia adelante)

---

### 2. Email de confirmación con acceso al registro
Al registrarse, el usuario debe recibir un correo que lo lleve a ver/gestionar su inscripción usando su `magic_token` existente.

**Verificar:** el email actual (enviado vía `background_tasks` con Resend) — ¿ya incluye este link? Si no, agregarlo al template.

---

### 3. Reordenar success.html — priorizar el pago
Ahora mismo no queda claro que falta pagar y subir comprobante. Cambiar el orden de la página:
- **Arriba de todo:** "Sube tu comprobante de pago" (acción pendiente)
- Debajo: confirmación de registro exitoso

---

### 4. Cambiar color verde en success.html
Verde comunica "proceso completado", pero el registro sigue pendiente de pago. Cambiar a un color neutro (azul o ámbar) para evitar que la gente piense que ya terminó.

---

### 5. Estados de registro más claros
Agregar/confirmar un campo de estado en el modelo `Registro` con estos valores:
```
1. Registrado - pago pendiente
2. Registrado - pago en revisión (al subir comprobante)
3. Registrado y pagado (al confirmar el pago)
```
Mostrar el estado actual de forma visible en el success.html y en cualquier vista de seguimiento del usuario (la que se accede vía magic_token).

---

## 🟡 Prioridad media

### 6. Responsive roto en iPhone 13 / iPhone XS
En success.html, la sección de información de transferencia bancaria se ve mal específicamente en estos modelos (390px y 375px de ancho respectivamente). Revisar anchos fijos en px en esa sección y convertir a unidades relativas / flexbox.

---

## 🟢 Prioridad baja

### 7. Verificar truncamiento de nombre completo
Caso reportado: "Hamlet Rodriguez" se guardó/mostró parcialmente ("Rodriguez"). Revisar si hay algún límite de caracteres en el campo `nombre_completo` del modelo, o si el frontend está cortando el string en algún punto (ej: al mostrarlo en confirmación o email).

---

## Orden sugerido de implementación

1. Separar campo de contacto de emergencia (cambio de formulario + modelo)
2. Estados de registro + reordenar success.html + cambiar color verde (estos 3 van juntos porque tocan la misma página)
3. Verificar/agregar link de acceso en el email
4. Revisar truncamiento de nombre
5. Fix responsive iPhone 13/XS
