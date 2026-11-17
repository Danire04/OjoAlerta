# OjoAlerta · Interfaz Streamlit

Interfaz en español para analizar una imagen y una descripción del mismo incidente. Incluye identidad visual propia, diseño adaptable, navegación entre análisis/historial/guía, vista previa de la imagen, validación de entradas, comparación interactiva de modelos y descarga de informes JSON/CSV.

Las transiciones de navegación, controles y resultados respetan `prefers-reduced-motion`. Manrope se incluye localmente con su licencia abierta; la interfaz no depende de un servidor de fuentes.

Prototipo académico que combina un clasificador **visual** (CLIP ViT-B/32 + regresión logística Spark ML) con uno **textual** (tokenización + CountVectorizer + TF-IDF + regresión logística Spark ML). Recibe **una imagen y una descripción del mismo incidente**; presenta probabilidades para T01, T02, T03 y T06 con una ponderación demostrativa 50/50.

## Archivos incluidos

```text
OjoAlerta/
├── app.py
├── interface.py                    # Pantallas, navegación y gráficos
├── domain.py                       # Validación, historial e informes
├── inference.py                    # Inferencia original, sin cambios
├── assets/                         # Identidad, estilos y tipografía
├── .streamlit/config.toml           # Tema y límite de carga
├── tests/                          # Pruebas de interfaz y dominio
├── requirements.txt
├── packages.txt
├── comprobar_modelos.py
├── 01_visual/modelos/
│   ├── visual_spark_pipeline/         # Modelo original Spark ML
│   └── visual_spark_metadata.json
└── 02_textual/modelos/
    ├── text_spark_pipeline/           # Modelo original Spark ML
    └── text_spark_metadata.json
```

Las dos carpetas `*_spark_pipeline/` deben mantenerse **completas**, incluyendo los directorios `stages/`, `metadata/` y sus archivos `.parquet`. Los archivos `.parquet` que contienen son **parte del modelo**: no deben borrarse. Las carpetas de videos, anotaciones y datos de entrenamiento no hacen falta para realizar inferencias.

## Prueba local (opcional)

Con **Python 3.10 o posterior y Java 17 o posterior** instalados, dentro del proyecto:

```bash
pip install -r requirements.txt
python comprobar_modelos.py
python -m streamlit run app.py
```

`python comprobar_modelos.py` realiza pruebas locales de estructura y metadatos, sin instalar Spark ni ejecutar CLIP. **No sustituye** la prueba de carga real del modelo con PySpark y el uso de la aplicación en el servidor final.

En Windows puedes ejecutar `iniciar.cmd` después de instalar las dependencias. Si existe un entorno `.venv`, lo utiliza automáticamente. Para crear uno:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

La primera inferencia puede descargar CLIP (`openai/clip-vit-base-patch32`). Para trabajar con una copia local, colócala en `01_visual/modelos/clip_preentrenado/`. `OJOALERTA_ROOT` permite usar los modelos desde otra ubicación. La aplicación carga los modelos solamente cuando pulsas **Analizar incidente**.

## Uso

1. Carga una imagen JPG/PNG de hasta 10 MB y 30 millones de píxeles.
2. Describe el mismo incidente y confirma la correspondencia de ambas señales.
3. Pulsa **Analizar incidente**. Revisa las probabilidades combinadas, la comparación de modelos o la tabla.
4. Descarga el informe o vuelve al caso desde **Historial**. Cambiar la imagen o el texto requiere analizar otra vez; el resultado anterior permanece en el historial.

Las entradas se conservan al cambiar de pantalla. El historial mantiene hasta 20 casos, con miniaturas, únicamente en la memoria de la sesión. Repetir el mismo caso lo actualiza sin duplicarlo. No se crea una base de datos ni se guardan automáticamente las imágenes en disco. Los archivos se procesan en el servidor donde se ejecute Streamlit.

## Pruebas y alcance de la verificación

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Se verificaron 15 pruebas de validación de imagen, orientación EXIF, combinación 50/50, exportaciones, límite y duplicación del historial, navegación, conservación de entradas, invalidación de resultados y recuperación ante errores. Las pruebas de interacción usan respuestas simuladas del predictor; **no prueban la inferencia real ni la precisión de los modelos**. La estructura y los metadatos de los modelos también se verificaron. Los 24 archivos de modelos y el código original de inferencia se compararon con el ZIP de origen.

Se inspeccionó la interfaz en escritorio y móvil (1440 y 390 px de ancho). En el equipo de desarrollo se detectó Java 8, insuficiente para Spark 4; para ejecutar los modelos debe instalarse Java 17 o posterior junto con las dependencias de `requirements.txt`. La vista de la interfaz puede abrirse sin iniciar Spark o descargar CLIP.

## Interpretación

La ponderación 50/50 es demostrativa y no está calibrada con pares verificados. T01 y T06 son aproximaciones semánticas de las clases textuales, como indica el archivo de metadatos. Las probabilidades no son certezas jurídicas ni una medida de gravedad. Uso académico: no utilizar para decisiones reales de seguridad ni identificación de responsables.
