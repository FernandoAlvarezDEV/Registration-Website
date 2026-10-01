# 📱 Plan Exhaustivo de Diseño Responsive - Onda Fest 2026

Este documento detalla una estrategia completa y sistemática para garantizar que las páginas de Onda Fest se visualicen de forma impecable tanto en dispositivos móviles, tablets, como en pantallas de escritorio, manteniendo la riqueza visual y estética actual.

---

## 1. 📏 Estrategia de Breakpoints (Puntos de Ruptura)

Implementaremos un enfoque "Desktop-first" ajustando mediante `max-width` (o "Mobile-first" si se prefiriera reescribir, pero para mantener tu CSS actual, `max-width` es la ruta más segura).

- **Escritorio Grande (1200px+):** Layout base actual.
- **Tablets y Laptops pequeñas (max-width: 1024px):** Transición inicial, márgenes reducidos.
- **Tablets en vertical (max-width: 768px):** Cambio de rejillas complejas a columnas más simples.
- **Móviles Grandes (max-width: 600px):** Layout de 1 sola columna pura, optimización de botones y modales.
- **Móviles Pequeños (max-width: 480px):** Ajuste de fuentes y padding ultra-compacto.

---

## 2. 🌍 Ajustes Globales (Tipografía y Espaciados)

1. **Tipografía Fluida:** Reducir los tamaños de encabezados (`h1`, `h2`) usando unidades relativas o media queries. 
   - Ejemplo: Un `h1` de `4rem` en PC debería bajar a `2.5rem` en móviles para no romper líneas.
2. **Paddings y Márgenes:** Las secciones que tienen `padding: 80px 40px` en PC, deben escalar a `padding: 40px 20px` en teléfonos.
3. **Botones:** Asegurar que los botones principales (`btn-primary`, `btn-login`) ocupen el `100%` del ancho en pantallas móviles para facilitar el uso con un solo dedo ("touch targets").

---

## 3. 🏠 Página de Inicio / Registro (`index.html`)

### A. Hero Section (Banner principal)
- **PC:** Texto gigante, alineado, con decoraciones (cintas amarillas, imágenes flotantes).
- **Tablet/Móvil:** 
  - Reducir el tamaño de la cinta amarilla rotada (transform y font-size menores).
  - Escalar la imagen/logo principal.
  - Asegurar que los botones de "Inscríbete" y "Ver detalles" pasen de estar uno al lado del otro (`flex-row`) a estar uno encima del otro (`flex-col`) en pantallas muy estrechas.

### B. Formulario de Inscripción (Container)
- **Grid de Campos:** Actualmente el formulario usa `grid-template-columns: 1fr 1fr` (2 columnas) para campos como Nombre/Teléfono.
  - **Acción (max-width: 768px):** Cambiar a `grid-template-columns: 1fr` (1 sola columna). Todos los inputs ocuparán todo el ancho.
- **Contenedores de Pago:** Las tarjetas con datos del Banco Popular deben acomodarse apiladas en vertical en lugar de una grilla horizontal.
- **Sombras:** Reducir ligeramente la propiedad `box-shadow` (ej. de `8px 8px 0` a `4px 4px 0`) en móviles para ahorrar espacio en los bordes de la pantalla.

---

## 4. 👤 Panel de Usuarios (`dashboard.html`)

### A. Cabecera (Header)
- Ocultar el nombre del usuario si la pantalla es muy pequeña y mostrar únicamente el icono de "Cerrar Sesión", o bien crear un header en dos líneas.

### B. Tarjetas Resumen (Ticket y Event Reminder)
- **Ticket Card:** Los 3 bloques (Código, Estado, Fecha) y el ícono de la Custodia flotante actualmente están en una fila. 
  - **Acción:** Pasar a apilamiento vertical (`flex-col`). Ocultar el ícono flotante de la Custodia en móviles muy pequeños para limpiar el espacio visual.
- **Cards Grid (Datos Personales y Detalles):** 
  - **PC:** `grid-template-columns: repeat(2, 1fr)`
  - **Acción (max-width: 768px):** Cambiar a `1fr` (una columna). La tarjeta de "Datos Personales" quedará arriba de "Detalles de Inscripción".

### C. Zona de Subida de Comprobante
- Mantener la zona de "drag & drop", pero aumentar el tamaño del ícono de subida y del botón "Subir Comprobante" para que sea muy fácil de tapar en móvil. Reducir padding interno del recuadro punteado.

---

## 5. 🛡️ Panel de Administración (`admin.html`)

*Nota: Los paneles de administración con tablas anchas son el mayor desafío en responsive web design.*

### A. Tarjetas de Estadísticas (Stats)
- **PC:** 4 tarjetas en fila (`grid-template-columns: repeat(4, 1fr)`).
- **Tablet:** 2x2 (`grid-template-columns: repeat(2, 1fr)`).
- **Móvil:** 1 columna (`grid-template-columns: 1fr`).

### B. La Tabla de Registros
*Como decidiste conservar las 11 columnas originales, una tabla no cabrá físicamente en un teléfono. Tenemos 2 soluciones híbridas que aplicaremos combinadas:*
1. **Contenedor con Scroll (Lo Actual):** Permitir el `overflow-x: auto` pero estilizaremos la barra de desplazamiento para que sea delgada, estética e intuitiva (con indicador visual de "desliza a la derecha 👉").
2. **Transformación a Tarjetas (Mobile Card View):** 
   - A los `max-width: 768px`, ocultaremos los `<thead>` tradicionales.
   - Cada `<tr>` (fila) se transformará en un bloque (tarjeta blanca con borde y sombra).
   - Cada `<td>` usará `display: flex; justify-content: space-between;` agregando un seudo-elemento (`::before`) que funcione como título (ej. "Nombre:", "Edad:").
   - *Este es el estándar de oro para tablas responsivas en administración.*

### C. Filtros y Búsqueda
- El buscador debe ocupar el 100% del ancho (`width: 100%`) antes que los botones de Acción (Actualizar, Salir).
- Los "filtros minimalistas" que acabamos de agregar a los encabezados deberán funcionar perfectamente en la vista de tarjetas móvil.

---

## 6. ✅ Pantalla de Éxito (`success.html`)
- Centrar todo el contenido.
- Reducir el padding de la tarjeta central.
- Ajustar el tamaño del botón flotante de WhatsApp.

---

## 7. 🚀 Resumen del Plan de Implementación

Si decides que apliquemos este plan, estos serán los pasos técnicos a ejecutar:
1. **Paso 1:** Añadir etiquetas `<meta name="viewport" content="width=device-width, initial-scale=1.0">` en todas las páginas (ya están presentes, pero validaremos su formato).
2. **Paso 2:** Crear una sección `@media` centralizada en cada archivo CSS (o dentro de cada archivo `.html`).
3. **Paso 3:** Aplicar conversión de Grids a Flex-columns en `index.html` y `dashboard.html`.
4. **Paso 4:** Aplicar la **vista de tarjetas** para la súper tabla en `admin.html` (para no tener que sufrir la barra horizontal en celulares).
5. **Paso 5:** Pruebas y refinamiento estético de sombras y tipografías móviles.

**Estatus:** *Pendiente de aprobación.*
