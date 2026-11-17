---
name: OjoAlerta
description: "Cada señal cuenta: una mesa de análisis clara para conectar imagen y descripción."
colors:
  accent: "#BC4535"
  accent-hover: "#A73729"
  accent-soft: "#F9EAE6"
  accent-strong: "#9C392D"
  ink: "#172B38"
  muted: "#526370"
  canvas: "#F6F7F9"
  surface: "#FFFFFF"
  line: "#DCE3E8"
  soft-surface: "#F3F5F7"
  neutral-tint: "#EDF1F4"
  neutral-label: "#405461"
  input-surface: "#FBFCFD"
  success: "#256747"
  chart-text: "#527E8C"
  chart-alternative: "#A7BBC5"
  chart-grid: "#E1E7EB"
typography:
  display:
    fontFamily: "Manrope, sans-serif"
    fontSize: "2.35rem"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "-0.035em"
  display-mobile:
    fontFamily: "Manrope, sans-serif"
    fontSize: "1.85rem"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Manrope, sans-serif"
    fontSize: "1.35rem"
    fontWeight: 750
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Manrope, sans-serif"
    fontSize: "1.08rem"
    fontWeight: 750
    letterSpacing: "-0.015em"
  body:
    fontFamily: "Manrope, sans-serif"
    lineHeight: 1.65
  intro:
    fontFamily: "Manrope, sans-serif"
    fontSize: "0.95rem"
    lineHeight: 1.65
  label:
    fontFamily: "Manrope, sans-serif"
    fontSize: "0.7rem"
    fontWeight: 700
    letterSpacing: "0.08em"
  pill:
    fontFamily: "Manrope, sans-serif"
    fontSize: "0.7rem"
    fontWeight: 650
  button:
    fontFamily: "Manrope, sans-serif"
    fontWeight: 700
  textarea:
    fontFamily: "Manrope, sans-serif"
    fontSize: "0.91rem"
    lineHeight: 1.65
  chart:
    fontFamily: "Manrope, sans-serif"
    fontSize: "12px"
rounded:
  code: "4px"
  control: "8px"
  media: "9px"
  placeholder: "10px"
  surface: "14px"
  pill: "30px"
  circle: "50%"
spacing:
  space-8: "8px"
  space-12: "12px"
  inset-compact: "19px"
  space-20: "20px"
  inset-surface: "24px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    typography: "{typography.button}"
    rounded: "{rounded.control}"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
  navigation-item:
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "12px 14px"
  navigation-item-active:
    backgroundColor: "{colors.accent-soft}"
    textColor: "{colors.accent-strong}"
  pill:
    backgroundColor: "{colors.neutral-tint}"
    textColor: "{colors.neutral-label}"
    typography: "{typography.pill}"
    rounded: "{rounded.pill}"
    padding: "5px 10px"
  signal-card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.surface}"
    padding: "{spacing.inset-surface}"
  signal-card-compact:
    padding: "{spacing.inset-compact}"
  textarea:
    backgroundColor: "{colors.input-surface}"
    typography: "{typography.textarea}"
  result-banner:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.surface}"
    rounded: "{rounded.surface}"
    padding: "26px 28px"
  result-banner-mobile:
    padding: "21px"
---

# Design System: OjoAlerta

## Overview

**Creative North Star: "La mesa de análisis clara"**

OjoAlerta presenta una mesa de trabajo serena y legible. La tinta organiza la lectura; el coral guía la acción; el fondo frío separa las superficies blancas sin añadir peso. La densidad es moderada: títulos compactos, instrucciones breves y espacio suficiente para comparar dos señales del mismo incidente.

La identidad reúne el ojo geométrico existente, el nombre OjoAlerta y la frase «Cada señal cuenta.». Manrope local mantiene una voz continua en navegación, entradas y resultados. El idioma de la interfaz es español. El movimiento acompaña cambios de contexto y aparición de resultados; la preferencia de movimiento reducido elimina las animaciones y transiciones personalizadas.

Este documento captura la implementación de `assets/styles.css`, `interface.py`, `.streamlit/config.toml` y el logotipo existente, con contexto de `PRODUCT.md` y `.impeccable/direction.md`. Los tokens del frontmatter son normativos; los valores que Streamlit resuelve por defecto y no están fijados en estas fuentes no se convierten en tokens.

**Key Characteristics:**

- Tinta para jerarquía y lectura; coral para acción y selección.
- Superficies planas, bordes discretos y esquinas suaves.
- Imagen y descripción visibles como una pareja de señales.
- Tipografía local, cifras tabulares y etiquetas explícitas.
- Transiciones breves con respeto al movimiento reducido.

## Colors

La paleta combina una tinta azul profunda y un coral terroso con blancos y grises fríos de baja saturación.

### Primary

- **Coral de acción** (`accent`): acción primaria, fragmento «Alerta» de la marca, señal visual del gráfico y primera categoría en la vista combinada.
- **Coral profundo** (`accent-hover`): respuesta al pasar el puntero por una acción primaria habilitada.
- **Coral velado** (`accent-soft`) y **coral de lectura** (`accent-strong`): fondo y texto del destino de navegación seleccionado.

### Neutral

- **Tinta de análisis** (`ink`): texto principal, marca, etapa actual y superficie del resultado destacado.
- **Pizarra suave** (`muted`): instrucciones, leyendas y metadatos que acompañan la tarea.
- **Papel frío** (`canvas`) y **blanco de trabajo** (`surface`): fondo de aplicación y superficies principales.
- **Línea fría** (`line`): divisores y contornos de contenedores.
- **Niebla de apoyo** (`soft-surface`): vista previa vacía, fondo de imágenes y respuesta de navegación al puntero.
- **Gris de etiqueta** (`neutral-tint`) y **pizarra de etiqueta** (`neutral-label`): distintivo académico, códigos y lectura de gráficos.
- **Blanco de escritura** (`input-surface`): fondo del área de descripción.

### Estados y datos

- **Verde de preparación** (`success`): texto de entradas listas y número de etapa completada. La preparación también se comunica con texto y forma.
- **Azul de señal textual** (`chart-text`): serie «Texto» en la comparación. La serie «Imagen» usa coral y «Combinación» usa tinta.
- **Azul de alternativa** (`chart-alternative`): categorías restantes en la vista combinada.
- **Cuadrícula fría** (`chart-grid`): referencias del eje porcentual.

**The Señal con contexto Rule.** Mantener etiquetas de texto junto al color de estados y series; un color aislado no expresa preparación ni identifica un modelo.

## Typography

**Display Font:** Manrope (con `sans-serif`).

**Body Font:** Manrope (con `sans-serif`).

**Character:** Una sola familia geométrica de trazos abiertos da continuidad a la mesa de trabajo. El archivo variable local cubre el intervalo declarado (200–800) y se carga con `font-display: swap`.

### Hierarchy

- **Display:** títulos de página; usa `display` y cambia a `display-mobile` en el punto de adaptación móvil. Su peso alto y espaciado negativo concentran la jerarquía sin aumentar la densidad.
- **Headline:** títulos de las señales y secciones; usa `headline`.
- **Title:** encabezados de la guía; usa `title`.
- **Body:** párrafos y listas con interlínea amplia; usa `body`. El tamaño general heredado de Streamlit no está fijado por el CSS personalizado.
- **Intro:** introducción de página; usa `intro`, con ancho máximo de lectura (67ch). La guía permite hasta (70ch).
- **Label:** encabezado lateral en mayúsculas; usa `label`. El distintivo académico usa `pill` y evita el espaciado ampliado del encabezado.
- **Datos:** gráficos con `chart`; porcentajes, contadores y tablas usan cifras tabulares cuando la implementación lo declara. El porcentaje destacado usa tamaño (1.8rem), peso (750) y espaciado (-0.03em).

**The Una voz Rule.** Mantener Manrope local en títulos, controles y lectura de datos; no introducir otra familia de exhibición en las pantallas existentes.

## Layout

El modo es **Operate**: navegación lateral, tarea principal y lectura del resultado en el mismo espacio. El contenedor principal limita el ancho (1240px), con relleno de escritorio (2.8rem 3rem 2rem). La barra lateral blanca se separa mediante una línea vertical; su contenido usa relleno (2.1rem 1.4rem 1.4rem).

En análisis, imagen y descripción ocupan dos columnas de igual proporción con separación nativa `medium`. El historial combina filtros en proporción (2:1) y detalle en proporción (1:1.8). Son relaciones de composición, no nuevos tokens de espaciado de Streamlit.

En anchos de hasta (1100px), el relleno principal cambia a (2.7rem 1.8rem 2rem), las tarjetas se compactan y la zona de carga admite ajuste de línea. En anchos de hasta (700px), el relleno cambia a (3.5rem 1rem 1.5rem), los títulos se reducen y el resultado usa su variante compacta. Las columnas se apilan y la navegación se pliega mediante el comportamiento adaptable nativo de Streamlit; no se fija aquí un punto adicional que el proyecto no declara.

El ritmo alterna separaciones pequeñas entre piezas relacionadas y rellenos mayores en superficies de trabajo. Los pasos se limitan a un ancho (660px); la vista previa conserva proporción con `object-fit: contain` y altura máxima (350px).

La llegada de una página dura (240ms) con desplazamiento inicial (5px). Los resultados usan una entrada de (440ms) con desplazamiento inicial (9px). Ambas usan la curva `ease-standard` del sidecar. No hay transición animada en Plotly: su duración está fijada en (0ms).

## Elevation & Depth

El CSS personalizado no define sombras. La profundidad se expresa con fondo frío, superficies blancas, contornos finos y el bloque de resultado en tinta. El foco visible es un contorno funcional, no una sombra de elevación. Los estilos nativos que no están sobrescritos siguen perteneciendo a Streamlit.

**The Superficie clara Rule.** Conservar la separación por tono y borde en los contenedores documentados; no sustituirla por una sombra añadida.

## Shapes

Las superficies principales usan la curva `surface`; navegación y botones usan `control`; imágenes, carga y alertas usan `media`. El vacío de imagen emplea `placeholder`; los códigos emplean `code`; el distintivo emplea `pill`. Círculos pequeños señalan preparación y avance. El logotipo conserva el ojo geométrico y su contenedor de esquinas suaves.

Los bordes de tarjetas y divisores son finos (1px). La carga de imagen se distingue por un contorno discontinuo; el resultado entra con recorte redondeado, conservando la forma de la superficie.

## Components

### Buttons

Directos, legibles y con una respuesta breve.

- **Shape:** curva `control` y altura mínima (42px); el CSS no fija un relleno propio para botones nativos.
- **Primary:** coral de acción, texto blanco y peso de `button`.
- **Hover / Focus:** coral profundo al pasar el puntero; contorno coral semitransparente (3px), separado (3px), al recibir foco de teclado. Fondo, borde y desplazamiento responden en (180ms).
- **Active:** desplazamiento hacia abajo (1px) durante la pulsación habilitada.
- **Secondary / Download:** conservan la variante nativa de Streamlit y comparten curva, altura mínima, foco y respuesta de pulsación; no se inventan colores o rellenos nativos.

### Chips

El distintivo académico es informativo y compacto. Usa los tokens `pill`, un punto circular (6px) y separación (7px). No funciona como filtro ni botón y no tiene un estado seleccionado inventado.

### Cards / Containers

Superficies tranquilas que agrupan cada señal.

- **Corner Style:** `surface`.
- **Background:** blanco de trabajo.
- **Shadow Strategy:** separación tonal y borde, como en Elevation & Depth.
- **Border:** línea fría (1px).
- **Internal Padding:** `inset-surface`; variante `inset-compact` en anchos de hasta (1100px).
- **Empty:** la imagen vacía usa niebla de apoyo, icono lineal, texto centrado y altura mínima (175px). El historial vacío usa una superficie blanca con borde e instrucción de continuidad.

### Inputs / Fields

La descripción se presenta como un campo amplio, con `textarea` y una altura configurada (235px). Su cursor usa coral de acción y el foco de teclado conserva el contorno común. Los contadores se alinean a la derecha con cifras tabulares.

La carga de imagen usa fondo frío, contorno discontinuo (1px), curva `media` y respuesta de fondo/borde en (180ms). Mantiene los textos «Arrastra aquí tu imagen», «JPG o PNG · hasta 10 MB» y «Elegir imagen». El error explica cómo recuperarse mediante una alerta nativa; el proyecto no añade un estilo de error de campo propio.

### Navigation

La navegación lateral contiene «Analizar incidente», «Historial» y «Cómo funciona». Cada destino ocupa todo el ancho, con relleno `navigation-item`. El destino activo combina coral velado y coral de lectura; el puntero usa niebla de apoyo. El foco se dibuja alrededor de la etiqueta (3px), separado (2px). La transición de fondo y texto dura (180ms). En móvil, se utiliza el panel lateral plegable de Streamlit.

### Pareja de señales y progreso

Imagen y descripción se muestran juntas antes del análisis. Los pasos «Prepara las señales», «Analiza» y «Revisa el resultado» usan círculos y conectores finos. La etapa actual combina tinta y blanco; las completadas usan un tratamiento verde suave. El estado de preparación se comunica además con una frase explícita. Al cambiar una entrada, se deja de presentar como actual el resultado que pertenece al par anterior.

### Resultado y comparación

El resultado destacado usa `result-banner`: tinta, título blanco, código coral claro y porcentaje tabular. Su entrada dura (440ms); en móvil se compactan relleno y título. La vista de probabilidades ofrece combinación, comparación de modelos y tabla. Los gráficos mantienen eje de (0–100 %) con intervalos de (25 %), etiquetas de categoría y porcentajes; las series conservan los colores descritos en Colors.

**The Movimiento opcional Rule.** Con `prefers-reduced-motion: reduce`, eliminar animaciones y transiciones personalizadas y mantener desplazamiento automático. Ninguna información debe depender de la animación.

## Do's and Don'ts

### Do:

- **Do** usar tinta, coral y superficies frías con las funciones del frontmatter.
- **Do** conservar Manrope local, el ojo geométrico y la interfaz en español.
- **Do** mostrar etiquetas junto al color de estados y series.
- **Do** conservar el foco visible y respetar el movimiento reducido.
- **Do** mantener imagen y descripción como una pareja visible y apilable.
- **Do** mantener porcentajes y contadores alineables con cifras tabulares.

### Don't:

- **Don't** añadir sombras a las superficies documentadas.
- **Don't** convertir el color de una probabilidad en una medida visual de gravedad.
- **Don't** ocultar el foco ni usar movimiento como único medio de comunicar un cambio.
- **Don't** presentar como vigente un resultado que corresponde a entradas anteriores.
- **Don't** convertir valores nativos no fijados de Streamlit en tokens supuestamente extraídos.
