"""Verificación estática de empaquetado OjoAlerta (no ejecuta Spark)."""
from pathlib import Path
import json
import ast

ROOT = Path(__file__).resolve().parent

MODELOS = [
    ("01_visual/modelos/visual_spark_pipeline", "org.apache.spark.ml.PipelineModel", 1),
    ("02_textual/modelos/text_spark_pipeline", "org.apache.spark.ml.PipelineModel", 4),
]


def leer_metadatos_spark(carpeta):
    documentos = list((carpeta / "metadata").glob("part-*.txt"))
    assert len(documentos) == 1, f"Metadatos Spark incorrectos: {carpeta}"
    return json.loads(documentos[0].read_text(encoding="utf-8"))


def main():
    ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    print("✓ app.py: sintaxis válida")
    for rel, clase, etapas in MODELOS:
        carpeta = ROOT / rel
        assert carpeta.is_dir(), f"Falta modelo: {carpeta}"
        meta = leer_metadatos_spark(carpeta)
        assert meta["class"] == clase
        assert len(meta["paramMap"]["stageUids"]) == etapas
        stages = list((carpeta / "stages").iterdir())
        assert len(stages) == etapas
        for stage in stages:
            assert (stage / "metadata").is_dir(), f"Falta metadata: {stage}"
            assert any((stage / "metadata").glob("part-*.txt"))
            if (stage / "data").is_dir():
                assert any((stage / "data").glob("*.parquet")), f"Faltan coeficientes: {stage}"
        print(f"✓ {rel}: {etapas} etapa(s) guardada(s)")

    v = json.loads((ROOT / "01_visual/modelos/visual_spark_metadata.json").read_text(encoding="utf-8"))
    t = json.loads((ROOT / "02_textual/modelos/text_spark_metadata.json").read_text(encoding="utf-8"))
    assert v["class_order"] == ["T01", "T02", "T03", "T06"]
    assert t["taxonomy_order"] == v["class_order"]
    assert t["legal_labels"] == ["Homicidio", "Hurto", "Lesiones", "Robo", "Robo agravado", "Tenencia ilegal de armas"]
    assert t["mapping"]["Tenencia ilegal de armas"] == "T06"
    print("✓ Metadatos visual y textual coherentes")
    print("Correcto: estructura lista para carga real y despliegue.")


if __name__ == "__main__":
    main()
