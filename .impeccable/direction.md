# OjoAlerta — interfaz Streamlit

## Scope and mode
Operate. Analizar un incidente, historial y guía. Se mantiene la inferencia original.

## Audience and job
Persona que presenta o evalúa el prototipo académico, inferida del repositorio y la petición. Debe cargar una imagen, describir el mismo hecho, confirmar correspondencia y entender cuatro probabilidades.

## Direction
Mesa de análisis clara: fondo frío muy suave, blanco para las entradas, azul tinta para lectura y coral para la acción. Logotipo de ojo geométrico. Manrope local con licencia abierta. Sin fotografía decorativa ni estadísticas inventadas.

## First viewport
Navegación y taxonomía a la izquierda; tarea y progreso arriba; imagen y descripción juntas en dos columnas. Controles nativos con estados claros. En móvil se apilan y la navegación se pliega.

## Signature interaction
La pareja imagen/texto define la identidad del análisis. Cambiar cualquiera invalida la lectura visible sin borrar el historial. La transición entre páginas dura 240 ms; el resultado entra en 440 ms; botones y selección responden en 180 ms. prefers-reduced-motion desactiva todo movimiento personalizado.

## Proof and constraints
15 pruebas funcionales con AppTest y datos simulados, sin inferencia real; verificación estática de modelos. Capturas desktop.jpg (1440×1000) y mobile.jpg (390×844) en .impeccable/review, con ausencia de desbordamiento horizontal verificada. Sin comp de imagen: el usuario delegó la implementación y la herramienta de dirección no pudo ejecutarse por instalación ausente. Semilla no disponible; no se inventa una.

## Open decisions
Despliegue y audiencia fuera del contexto académico no confirmados. Java local detectado: 8; el backend Spark 4 necesita Java 17+. PySpark y CLIP no se cargaron en estas pruebas.
