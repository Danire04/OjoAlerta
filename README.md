# OjoAlerta · Aplicación de demostración

Prototipo académico que combina un clasificador **visual** (CLIP ViT-B/32 + regresión logística Spark ML) con uno **textual** (tokenización + CountVectorizer + TF-IDF + regresión logística Spark ML). Recibe **una imagen y una descripción del mismo incidente**; presenta probabilidades para T01, T02, T03 y T06 con una ponderación demostrativa 50/50.

## Archivos incluidos

```text
OjoAlerta/
├── app.py
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

Con Python y Java instalados, dentro del proyecto:

```bash
pip install -r requirements.txt
python comprobar_modelos.py
streamlit run app.py
```

`python comprobar_modelos.py` realiza pruebas locales de estructura y metadatos, sin instalar Spark ni ejecutar CLIP. **No sustituye** la prueba de carga real del modelo con PySpark y el uso de la aplicación en el servidor final.
