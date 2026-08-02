# Directrices de Diseño y Arquitectura Web - Onda Fest

## 1. Concepto Visual y Dirección de Arte
- **Estética**: Festival psicodélico retro, enérgico y moderno (vibe Coachella / Años 70) fusionado con iconografía espiritual audaz.
- **Atmósfera**: Comunidad, celebración, juventud y frescura espiritual.
- **Enfoque de UI/UX**: Diseño limpio de bloques de color (*color-blocking*), bordes definidos con esquinas suavizadas (`border-radius: 12px` a `16px`), y uso estratégico de íconos vectoriales planos como elementos de anclaje visual e identidad.

---

## 2. Sistema de Diseño (Tokens de Marca)

### A. Paleta de Colores (Códigos HEX Estrictos)
- **Fondo Base (Crema)**: `#F9F4E0` (Color predominante en la experiencia pública; genera el tono retro-cálido).
- **Marca Principal (Rojo)**: `#FF0000` (Logos, alertas críticas y textos de máximo contraste).
- **Enérgicos / Festival**:
  - Amarillo: `#FEB004` (Fondos de botones CTA y estados activos).
  - Naranja: `#FF7D04` (Acentos secundarios y gradientes en tarjetas).
  - Fucsia: `#ED008C` (Elementos interactivos alternativos y badges).
  - Verde Neón: `#3CE705` (Mensajes de éxito o confirmación en formularios).

### B. Tipografía Alternativa para Web
- **Títulos (Display)**: Si `Tan Songbird` no está cargada localmente, usar **"Syne"**, **"Clara"** o **"Chonburi"** (Google Fonts) en peso Extra-Bold/Black con interletrado ligeramente cerrado.
- **Cuerpo y UI**: `Open Sauce` (Alternativas web: **"Plus Jakarta Sans"** o **"Inter"**) en pesos Regular, Medium y Semi-Bold.

---

## 3. Guía de Uso para los Íconos Decorativos
Los íconos oficiales deben implementarse de forma puramente plana (*flat vector graphics*) integrados orgánicamente en el diseño:

1. **Custodia Festivalera (Amarillo Oro)**: Símbolo central de la temática religioso-Coachella. Debe usarse como remate visual en secciones informativas o como marca de agua sutil de fondo en los módulos de espiritualidad.
2. **Cámara de Cine Retro (Naranja)**: Se posiciona junto a las secciones de multimedia, galerías de fotos del evento anterior o adelantos de lo que se vivirá en Onda Fest.
3. **Micrófono de Mano (Rojo)**: Elemento de UI para identificar bloques relacionados con la música, las bandas en vivo, los conferencistas principales o las dinámicas de voz.
4. **Lentes de Sol de Festival (Naranja/Fucsia)**: Elemento lúdico ideal para la cabecera de registro de asistentes o decorando las esquinas del área de bienvenida.
5. **Cruz Estilizada (Fucsia)**: Iconografía de fe moderna. Utilízala como viñeta estilizada en listas de requisitos, esquinas de contenedores clave o en el pie de página.

---

## 4. Estructura de Páginas y Enrutamiento (Mapa de Archivos HTML)

La IA debe estructurar el diseño de la aplicación web conectando coherentemente los siguientes flujos de archivos:

### 📄 index.html (Página de Inicio / Landing Oficial)
- **Objetivo**: Capturar el impacto del festival y guiar al usuario hacia la conversión.
- **Estructura**:
  - *Hero Section*: Fondo crema `#F9F4E0`, logotipo masivo en Rojo `#FF0000`, y una marquesina infinita con el texto `ONDA FEST • UNA SOLA ONDA`.
  - *Grid Temático*: Bloques informativos decorados con el ícono de los **Lentes de sol** y el **Micrófono**.
  - *CTA Principal*: Botón gigante en Amarillo `#FEB004` con bordes redondeados pronunciados que apunte directamente a `inscripcion.html`.

### 📄 inscripcion.html (Formulario de Registro)
- **Objetivo**: Proceso de registro ágil y de alta conversión.
- **Estructura**:
  - Contenedor de formulario centrado sobre fondo crema, imitando la estética de una entrada física de festival.
  - Campos de texto (`inputs`) limpios. Al hacer foco (*focus*), el borde debe iluminarse en Naranja `#FF7D04` o Fucsia `#ED008C`.
  - Decoración: Encabezado del formulario acompañado por el ícono de la **Cruz fucsia** o la **Custodia** para asentar la temática.
  - Al completar con éxito la acción del botón de envío, el flujo redirige a `succes.html`.

### 📄 succes.html (Confirmación de Registro Completado)
- **Objetivo**: Validar el registro y generar entusiasmo en el usuario.
- **Estructura**:
  - Mensaje central de éxito en tipografía gigante: *"¡YA TIENES TU PASE!"*.
  - Uso del color Verde Neón `#3CE705` para estados o íconos de confirmación en pantalla.
  - Elementos visuales flotantes simulando confeti usando las formas vectoriales del brandbook (lentes, estrellas, cruces).
  - Botón de retorno al inicio (`index.html`) o enlace para descargar el boleto digital.

### 📄 Dashboard.html (Panel del Asistente / Usuario)
- **Objetivo**: Control del usuario registrado para ver sus datos de acceso.
- **Estructura**:
  - Interfaz de usuario más limpia pero manteniendo los colores de acento. Lateral izquierdo de navegación en color Crema oscuro o con bordes bien definidos.
  - Tarjetas resumen que muestran: Estado del ticket, cronograma del festival y código QR de acceso.

### 📄 Admin.html (Panel de Control y Métricas)
- **Objetivo**: Monitoreo de inscripciones y gestión de logística para los organizadores.
- **Estructura**:
  - Estructura corporativa pero con la identidad de Onda Fest en la barra superior.
  - Gráficos y tablas de analíticas que utilicen la paleta de colores para diferenciar las categorías (ej: Rojo para inasistencias, Verde para registros completados, Amarillo para pendientes).
  - Enlaces directos para exportar bases de datos y gestionar la lista de asistentes.

## 5. Directorio de Activos Locales (Assets)
Todos los recursos vectoriales se encuentran en la ruta raíz del proyecto bajo la carpeta: `Diseno/iconos/`

Rutas exactas de los archivos para vinculación en HTML:
- **Custodia Festivalera**: `Diseno/iconos/custodia.png` (o .png) -> Usar como marca de agua o separador espiritual.
- **Cámara de Cine Retro**: `Diseno/iconos/camara.png` (o .png) -> Usar en galerías y secciones multimedia.
- **Micrófono de Mano**: `Diseno/iconos/microfono.png` (o .png) -> Usar junto a bloques de bandas y oradores.
- **Lentes de Sol**: `Diseno/iconos/lentes.png` (o .png) -> Usar en la cabecera y el formulario de inscripción.
- **Cruz Estilizada**: `Diseno/iconos/cruz.png` (o .png) -> Usar como viñeta en listas y en el pie de página (footer).
