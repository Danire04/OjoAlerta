"""OjoAlerta: demo de fusión tardía de dos modelos Spark ML preentrenados.

Recibe una imagen y una descripción DEL MISMO incidente. No necesita
pares_verificados.csv para inferir. No atribuir métricas de prueba no calculadas.
"""
import hashlib
import io
import json
import os
import re
import shutil
import tempfile
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError

T = {"T01": "Agresión", "T02": "Robo", "T03": "Sustracción", "T06": "Disparos"}
ORDEN = list(T)
CLASES_TEXTO = [
    "Homicidio", "Hurto", "Lesiones", "Robo", "Robo agravado",
    "Tenencia ilegal de armas",
]
MAPEO_T = {
    "Homicidio": "T01", "Lesiones": "T01", "Robo": "T02",
    "Robo agravado": "T02", "Hurto": "T03",
    "Tenencia ilegal de armas": "T06",
}
ROOT = Path(os.getenv("OJOALERTA_ROOT", str(Path(__file__).resolve().parent))).expanduser().resolve()
ALPHA_VISUAL = 0.50  # demostrativo, NO optimizado con datos pareados


def norm_text(texto):
    texto = unicodedata.normalize("NFKD", str(texto or "").lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9ñ ]", " ", texto)).strip()


def normalizar(p):
    x = np.asarray(p, dtype=float).ravel()
    if not np.all(np.isfinite(x)) or x.min() < 0 or x.sum() <= 0:
        raise ValueError("Probabilidades inválidas devueltas por el modelo")
    return x / x.sum()


def ruta_modelo(nombre):
    origen = ROOT / nombre
    if not (origen / "metadata").is_dir():
        raise FileNotFoundError(f"Modelo Spark ML no encontrado: {origen}")
    # Spark local lee con más fiabilidad desde un directorio del propio Colab.
    huella = hashlib.sha256(str(origen).encode()).hexdigest()[:12]
    destino = Path(tempfile.gettempdir()) / "ojoalerta_app_modelos" / huella
    if not (destino / "metadata").is_dir():
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(origen, destino, dirs_exist_ok=True)
    return destino


@st.cache_resource(show_spinner="Iniciando Spark ML...")
def recursos_spark():
    from pyspark.sql import SparkSession
    from pyspark.ml import PipelineModel
    spark = (SparkSession.builder.master("local[2]")
             .appName("OjoAlertaFusionTardia")
             .config("spark.ui.enabled", "false")
             .config("spark.driver.memory", "1g")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    visual = PipelineModel.load(str(ruta_modelo("01_visual/modelos/visual_spark_pipeline")))
    texto = PipelineModel.load(str(ruta_modelo("02_textual/modelos/text_spark_pipeline")))
    # Los archivos fuente visual y textual usan la misma taxonomía de cuatro clases.
    meta_visual = ROOT / "01_visual/modelos/visual_spark_metadata.json"
    meta_texto = ROOT / "02_textual/modelos/text_spark_metadata.json"
    if meta_visual.is_file():
        info = json.loads(meta_visual.read_text(encoding="utf-8"))
        if info.get("class_order") != ORDEN:
            raise ValueError("Orden visual incompatible con T01/T02/T03/T06")
    if meta_texto.is_file():
        info = json.loads(meta_texto.read_text(encoding="utf-8"))
        if info.get("legal_labels") != CLASES_TEXTO or info.get("mapping") != MAPEO_T:
            raise ValueError("Clases o correspondencia textual incompatibles")
    return spark, visual, texto


@st.cache_resource(show_spinner="Cargando CLIP...")
def recursos_clip():
    import torch
    from transformers import CLIPModel, CLIPProcessor
    local = ROOT / "01_visual/modelos/clip_preentrenado"
    origen = str(local) if (local / "config.json").is_file() and (list(local.glob("*.safetensors")) or (local / "pytorch_model.bin").is_file()) else "openai/clip-vit-base-patch32"
    modelo = CLIPModel.from_pretrained(origen).eval()
    procesador = CLIPProcessor.from_pretrained(origen)
    dispositivo = "cpu"  # la app usa CPU para no competir con Colab/GPU
    return modelo.to(dispositivo), procesador, dispositivo


def predecir(imagen, descripcion):
    import torch
    from pyspark.ml.linalg import Vectors

    spark, visual, textual = recursos_spark()
    clip, procesador, dispositivo = recursos_clip()
    pixeles = procesador(images=imagen, return_tensors="pt")["pixel_values"].to(dispositivo)
    with torch.inference_mode():
        vector = clip.get_image_features(pixel_values=pixeles)
        if hasattr(vector, "pooler_output"):
            vector = vector.pooler_output
        elif isinstance(vector, tuple):
            vector = vector[0]
        vector = vector.detach().cpu().numpy().reshape(1, -1).astype("float32")
    if vector.shape != (1, 512):
        raise ValueError("CLIP no devolvió un embedding de 512 características")
    vector /= np.maximum(np.linalg.norm(vector, axis=1, keepdims=True), 1e-12)

    visual_df = spark.createDataFrame(
        [(Vectors.dense(vector[0].astype(float).tolist()),)], ["features"]
    )
    texto_df = spark.createDataFrame([(norm_text(descripcion),)], ["norm"])

    prob_visual = normalizar(
        visual.transform(visual_df).select("probability").first()[0].toArray()
    )
    prob_seis = normalizar(
        textual.transform(texto_df).select("probability").first()[0].toArray()
    )
    if len(prob_visual) != 4 or len(prob_seis) != 6:
        raise ValueError("Las dimensiones no coinciden con los modelos esperados")

    prob_textual = np.zeros(4, dtype=float)
    for i, clase in enumerate(CLASES_TEXTO):
        prob_textual[ORDEN.index(MAPEO_T[clase])] += prob_seis[i]
    prob_textual = normalizar(prob_textual)

    fusion = normalizar(ALPHA_VISUAL * prob_visual + (1 - ALPHA_VISUAL) * prob_textual)
    return prob_visual, prob_textual, fusion


st.set_page_config(page_title="OjoAlerta · Fusión tardía", page_icon="🛡️", layout="centered")
st.title("OjoAlerta")
st.caption("Fusión visual y textual · Prototipo académico")
st.info(
    "Esta versión combina los dos modelos Spark ML entrenados. "
    "No necesita pares_verificados.csv para analizar un caso nuevo."
)
with st.expander("Estado de archivos de los modelos"):
    for carpeta in (
        "01_visual/modelos/visual_spark_pipeline",
        "02_textual/modelos/text_spark_pipeline",
    ):
        disponible = (ROOT / carpeta / "metadata").is_dir()
        st.write(("✅ " if disponible else "❌ ") + carpeta)
    st.caption("Se usan modelos entrenados previamente; este sitio no los reentrena.")
st.warning(
    "El resultado es exploratorio: el peso 50/50 no ha sido calibrado ni "
    "la combinación evaluada con un conjunto de casos emparejados. "
    "Además, tenencia ilegal de armas no equivale a disparos."
)

with st.form("analisis"):
    archivo = st.file_uploader("Imagen del incidente", type=["png", "jpg", "jpeg"])
    descripcion = st.text_area(
        "Descripción del MISMO incidente",
        placeholder="Describe únicamente lo que sucede en esta imagen.",
        height=130,
    )
    confirmado = st.checkbox("Confirmo que el texto corresponde a la imagen proporcionada")
    ejecutar = st.form_submit_button("Clasificar incidente", type="primary")

if ejecutar:
    if archivo is None or not descripcion.strip():
        st.error("Selecciona una imagen y escribe una descripción.")
    elif not confirmado:
        st.error("Confirma que imagen y texto corresponden al mismo incidente.")
    elif len(archivo.getvalue()) > 10 * 1024 * 1024:
        st.error("El archivo supera el límite de 10 MB.")
    else:
        try:
            img = ImageOps.exif_transpose(Image.open(io.BytesIO(archivo.getvalue()))).convert("RGB")
            if img.width * img.height > 30_000_000:
                raise ValueError("Imagen demasiado grande")
            st.image(img, caption="Fotograma analizado", use_container_width=True)
            with st.spinner("Procesando con CLIP y Spark ML..."):
                pv, pt, pf = predecir(img, descripcion.strip())
            resultado = ORDEN[int(np.argmax(pf))]
            st.subheader(f"Categoría estimada: {resultado} · {T[resultado]}")
            tabla = pd.DataFrame([
                {"Categoría": f"{nombre} · {T[nombre]}",
                 "Visual": float(pv[i]), "Textual": float(pt[i]),
                 "Fusión 50/50": float(pf[i])}
                for i, nombre in enumerate(ORDEN)
            ])
            st.dataframe(
                tabla.style.format({"Visual": "{:.1%}", "Textual": "{:.1%}",
                                    "Fusión 50/50": "{:.1%}"}),
                hide_index=True, use_container_width=True,
            )
            st.bar_chart(tabla.set_index("Categoría"))
            st.caption("Las probabilidades son salidas de modelos, no certezas jurídicas ni calificaciones de gravedad.")
        except (ValueError, UnidentifiedImageError, FileNotFoundError) as error:
            st.error(str(error))
        except Exception as error:
            st.exception(error)

st.divider()
st.caption("No utilizar para decisiones reales de seguridad ni identificación de responsables.")
