"""Validación y resultados de la interfaz, sin iniciar modelos ni Java."""
from __future__ import annotations

import hashlib
import io
import json
import warnings
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
from PIL import Image, ImageOps, UnidentifiedImageError

from inference import T, ORDEN, normalizar

MAX_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 30_000_000
MAX_DESCRIPTION = 4000
HISTORY_LIMIT = 20


def decode_image(content: bytes) -> Image.Image:
    if len(content) > MAX_BYTES:
        raise ValueError("La imagen supera los 10 MB. Reduce su tamaño y vuelve a cargarla.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(content)) as image:
                if image.format not in {"JPEG", "PNG"}:
                    raise ValueError("Usa una imagen JPG o PNG; cambiar la extensión no convierte el archivo.")
                if image.width * image.height > MAX_PIXELS:
                    raise ValueError("La imagen supera los 30 millones de píxeles. Reduce su resolución.")
                return ImageOps.exif_transpose(image).convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        raise ValueError("No se pudo abrir la imagen. Vuelve a guardarla como JPG o PNG.") from error


def fingerprint(content: bytes, description: str) -> str:
    # Length prefix separates the two inputs unambiguously.
    digest = hashlib.sha256()
    digest.update(len(content).to_bytes(8, "big"))
    digest.update(content)
    digest.update(description.strip().encode("utf-8"))
    return digest.hexdigest()


def build_result(content, description, filename, visual, textual, elapsed):
    pv, pt = normalizar(visual), normalizar(textual)
    if len(pv) != 4 or len(pt) != 4:
        raise ValueError("El modelo debe devolver cuatro probabilidades por modalidad.")
    pf = normalizar(0.5 * pv + 0.5 * pt)
    output = io.BytesIO()
    image = decode_image(content)
    image.thumbnail((1200, 1200))
    image.save(output, format="JPEG", quality=85)
    return {
        "id": fingerprint(content, description),
        "created_at": datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec="seconds"),
        "filename": filename,
        "description": description.strip(),
        "visual": pv.tolist(), "textual": pt.tolist(), "fusion": pf.tolist(),
        "category": ORDEN[int(np.argmax(pf))],
        "elapsed": round(elapsed, 2), "thumbnail": output.getvalue(),
    }


def result_table(result):
    return pd.DataFrame({
        "Código": ORDEN,
        "Categoría": [T[code] for code in ORDEN],
        "Imagen": result["visual"],
        "Texto": result["textual"],
        "Combinación 50/50": result["fusion"],
    })


def export_json(result):
    report = {key: value for key, value in result.items() if key != "thumbnail"}
    report["weights"] = {"visual": 0.5, "textual": 0.5}
    report["categories"] = T
    report["model_versions"] = {"visual": "visual_spark_ml_v2", "textual": "text_spark_ml_v2"}
    report["scope"] = "Prototipo académico. Probabilidades no calibradas; T01 y T06 son proxies semánticos."
    return json.dumps(report, ensure_ascii=False, indent=2)


def result_csv(result):
    table = result_table(result)
    table.insert(0, "Fecha (-05:00)", result["created_at"])
    return table.to_csv(index=False).encode("utf-8-sig")


def add_to_history(history, result):
    # Re-running an identical case updates it, without duplicating it.
    return [result] + [item for item in history if item["id"] != result["id"]][:HISTORY_LIMIT - 1]
