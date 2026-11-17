import io
from pathlib import Path

import pytest
from PIL import Image
from streamlit.testing.v1 import AppTest

import interface

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def app():
    return AppTest.from_file(APP, default_timeout=20).run()


def button(app_test, label):
    return next(item for item in app_test.button if item.label == label)


def prepare_case(app_test):
    image = io.BytesIO()
    Image.new("RGB", (32, 24), "#526370").save(image, format="PNG")
    app_test.session_state["evidence"] = {"content": image.getvalue(), "name": "prueba.png"}
    app_test.run()
    app_test.text_area(key="_description").set_value("Una descripción de prueba.").run()
    app_test.checkbox(key="_confirmed").check().run()


def test_initial_screen_and_required_fields():
    test = app()
    assert not test.exception
    button(test, "Analizar incidente").click().run()
    assert "Añade una imagen" in test.error[0].value


def test_navigation_and_draft_survive_screen_changes():
    test = app()
    prepare_case(test)
    test.radio(key="route").set_value("Historial").run()
    assert test.title[0].value == "Historial de la sesión"
    button(test, "Analizar mi primer incidente").click().run()
    assert test.text_area(key="_description").value == "Una descripción de prueba."
    assert test.checkbox(key="_confirmed").value
    assert test.session_state["evidence"]["name"] == "prueba.png"
    test.radio(key="route").set_value("Cómo funciona").run()
    assert not test.exception
    assert len(test.dataframe[0].value) == 4


def test_analysis_history_reset_and_stale_result(monkeypatch):
    calls = []
    def fake_predictor(image, description):
        calls.append(description)
        return [.1, .6, .2, .1], [.2, .4, .3, .1], [.15, .5, .25, .1]
    monkeypatch.setattr(interface, "predecir", fake_predictor)
    test = app()
    prepare_case(test)
    button(test, "Analizar incidente").click().run()
    assert not test.exception
    assert len(calls) == 1
    assert test.session_state["active_result"]["category"] == "T02"
    assert len(test.session_state["history"]) == 1
    test.text_area(key="_description").set_value("Una descripción diferente.").run()
    assert not test.checkbox(key="_confirmed").value
    assert "Las entradas cambiaron" in test.info[0].value
    assert not test.get("plotly_chart")
    test.radio(key="route").set_value("Historial").run()
    assert not test.exception
    assert len(test.get("plotly_chart")) == 1
    test.text_input(key="history_query").set_value("no existe").run()
    assert "No hay análisis" in test.info[0].value
    test.radio(key="route").set_value("Analizar incidente").run()
    button(test, "Limpiar entradas").click().run()
    assert test.text_area(key="_description").value == ""
    assert test.session_state["active_result"] is None
    assert test.session_state["evidence"] is None
    assert len(test.session_state["history"]) == 1


def test_model_failure_shows_recovery_and_does_not_save(monkeypatch):
    def broken_model(*args):
        raise ModuleNotFoundError("No module named pyspark")
    monkeypatch.setattr(interface, "predecir", broken_model)
    test = app()
    prepare_case(test)
    button(test, "Analizar incidente").click().run()
    assert not test.exception
    assert "Falta una dependencia" in test.error[0].value
    assert not test.session_state["history"]
