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

## Subir a GitHub — modo sencillo

1. Descarga el ZIP preparado y **descomprímelo**. No subas el ZIP tal cual como único archivo del repositorio.
2. En tu repositorio `OjoAlerta`, pulsa **Add file → Upload files** y sube el contenido descomprimido, preservando las carpetas. Si GitHub no permite seleccionar las carpetas en tu navegador, usa GitHub Desktop para copiar el contenido y hacer *Commit → Push*.
3. Verifica que en GitHub exista `app.py` en la raíz y el archivo `01_visual/modelos/visual_spark_pipeline/metadata/part-...txt` dentro del modelo.
4. En [Streamlit Community Cloud](https://share.streamlit.io), crea una aplicación desde ese repositorio y configura `app.py` como **Main file path**. Selecciona Python 3.11 o 3.12 si está disponible. Para repositorio privado tendrás que conceder a Streamlit permiso de acceso.

**Advertencia de recursos:** Spark ML crea un proceso Java y CLIP carga PyTorch + Transformers. Puede exceder los límites gratuitos de memoria/CPU de Streamlit Community Cloud. El paquete está preparado para intentarlo, no garantiza que allí alcance a funcionar. Si no carga, puede ejecutarse en una computadora con suficiente memoria o en un servidor con más recursos, sin cambiar las rutas de los modelos.

## Prueba local (opcional)

Con Python y Java instalados, dentro del proyecto:

```bash
pip install -r requirements.txt
python comprobar_modelos.py
streamlit run app.py
```

Si los modelos están en otra carpeta, configura la variable de entorno `OJOALERTA_ROOT` apuntando al directorio que contiene `01_visual/` y `02_textual/`. No es necesaria en el repositorio que acompaña este README.

## Limitaciones técnicas y académicas

- Los modelos suministrados son los **originales**; el empaquetado no los reentrena ni corrige la precisión.
- La fusión 50/50 **no está calibrada ni evaluada** con un conjunto independiente de pares imagen-texto del mismo evento.
- Las salidas son estimaciones del modelo, no probabilidades jurídicas ni decisiones automatizadas de seguridad.
- El conjunto textual de origen es **sintético**. Agregar sus probabilidades a T01/T02/T03/T06 utiliza equivalencias aproximadas; en particular, `Tenencia ilegal de armas` **no significa** `Disparos`.
- El rendimiento visual previamente reportado por el proyecto fue bajo (F1-macro alrededor de 0.31); la aplicación es un prototipo de demostración, **no** un sistema validado para uso operativo.

## Verificación

`python comprobar_modelos.py` realiza pruebas locales de estructura y metadatos, sin instalar Spark ni ejecutar CLIP. **No sustituye** la prueba de carga real del modelo con PySpark y el uso de la aplicación en el servidor final.
