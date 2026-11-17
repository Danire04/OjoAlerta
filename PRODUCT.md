# OjoAlerta

<!-- impeccable:product-schema 1 -->

## Platform
web

## Product Purpose
Prototipo académico para clasificar una imagen y una descripción del mismo incidente mediante dos modelos preentrenados. El usuario pidió una interfaz Streamlit comprensible, interactiva, con identidad propia, animaciones y transiciones.

## Operating Context
Se carga una imagen PNG/JPEG de hasta 10 MB y una descripción, y se confirma que ambas corresponden al mismo incidente. El resultado compara cuatro categorías y las salidas de ambos modelos.

## Capabilities and Constraints
Se conserva el código de inferencia original en inference.py: CLIP ViT-B/32 (512 características), pipeline visual Spark ML y pipeline textual Spark ML de seis clases, mapeado a T01/T02/T03/T06. Fusión demostrativa 50/50, sin calibración con pares verificados. Los metadatos señalan que T01 y T06 son proxies semánticos. No se inventan métricas de precisión. Los archivos parquet son parte de los modelos y se conservan.

Historial limitado a la sesión del navegador y exportación explícita por el usuario. No se agregan servicios externos de almacenamiento. Público primario inferido: quien presenta o evalúa el prototipo académico; no hay otros roles confirmados.

## Brand Commitments
Nombre OjoAlerta. Idioma español. El usuario delegó el diseño y pidió transiciones que faciliten la navegación.

## Evidence on Hand
README.md, app.py original, comprobar_modelos.py y modelos/metadatos incluidos en 01_visual y 02_textual. Fuente descargada desde la sesión autorizada de GitHub, rama main, commit 6086f2a04157c11e2caf240f6f129b78b00e7637.

## Product Principles
- Mostrar imagen y descripción juntas antes del análisis.
- Distinguir probabilidades del modelo de certezas sobre un hecho.
- Mantener resultados ligados a las entradas que los produjeron.
- Explicar los errores con una forma de recuperarse.
- Respetar navegación por teclado y movimiento reducido.
