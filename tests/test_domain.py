import io
import json

import numpy as np
import pytest
from PIL import Image

from domain import (
    MAX_BYTES, add_to_history, build_result, decode_image, export_json,
    fingerprint, result_csv,
)


@pytest.fixture
def image_bytes():
    output = io.BytesIO()
    Image.new("RGB", (32, 24), "#526370").save(output, format="PNG")
    return output.getvalue()


@pytest.fixture
def result(image_bytes):
    return build_result(image_bytes, "Descripción de prueba", "prueba.png", [.1, .6, .2, .1], [.2, .4, .3, .1], 1.5)


@pytest.mark.parametrize("content", [b"", b"not an image", b"\x89PNG\r\ninvalid"])
def test_rejects_unreadable_images(content):
    with pytest.raises(ValueError, match="No se pudo abrir"):
        decode_image(content)


def test_checks_byte_limit_before_decoding():
    with pytest.raises(ValueError, match="10 MB"):
        decode_image(b"x" * (MAX_BYTES + 1))


def test_rejects_gif_even_with_png_filename():
    output = io.BytesIO()
    Image.new("RGB", (12, 12)).save(output, format="GIF")
    with pytest.raises(ValueError, match="JPG o PNG"):
        decode_image(output.getvalue())


def test_normalizes_orientation_before_preview():
    output = io.BytesIO()
    image = Image.new("RGB", (24, 12))
    exif = image.getexif()
    exif[274] = 6
    image.save(output, format="JPEG", exif=exif)
    assert decode_image(output.getvalue()).size == (12, 24)


def test_result_is_exact_mean_and_preserves_class_order(result):
    np.testing.assert_allclose(result["fusion"], [.15, .5, .25, .1])
    assert result["category"] == "T02"


def test_result_rejects_invalid_model_output(image_bytes):
    with pytest.raises(ValueError):
        build_result(image_bytes, "Prueba", "a.png", [np.nan, 0, 0, 0], [.25] * 4, 1)


def test_export_has_numeric_probabilities_and_no_image(result):
    report = json.loads(export_json(result))
    assert "thumbnail" not in report
    assert isinstance(report["fusion"][0], float)
    assert sum(report["fusion"]) == pytest.approx(1)
    assert report["weights"] == {"visual": .5, "textual": .5}
    csv = result_csv(result).decode("utf-8-sig")
    assert "T01,Agresión" in csv
    assert result["description"] not in csv


def test_history_deduplicates_same_case_and_limits_memory(result):
    history = []
    for index in range(25):
        history = add_to_history(history, dict(result, id=str(index)))
    assert len(history) == 20
    assert history[-1]["id"] == "5"
    history = add_to_history(history, dict(result, id="12", elapsed=7))
    assert len(history) == 20
    assert history[0]["elapsed"] == 7
    assert len([item for item in history if item["id"] == "12"]) == 1


def test_result_identity_changes_with_either_input(image_bytes):
    assert fingerprint(image_bytes, "A") != fingerprint(image_bytes, "B")
    assert fingerprint(image_bytes, "A") != fingerprint(image_bytes + b"more", "A")
    assert fingerprint(image_bytes, " A ") == fingerprint(image_bytes, "A")
