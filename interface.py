"""Interfaz Streamlit de OjoAlerta; inferencia original en inference.py."""
from __future__ import annotations

import base64
import json
import logging
import time
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from domain import (
    HISTORY_LIMIT, MAX_DESCRIPTION, add_to_history, build_result, decode_image,
    export_json, fingerprint, result_csv, result_table,
)
from inference import ORDEN, ROOT, T, predecir

LOCAL = Path(__file__).resolve().parent
LOGGER = logging.getLogger(__name__)


@st.cache_data(show_spinner=False)
def stylesheet(css, font):
    return css.replace("__FONT__", base64.b64encode(font).decode("ascii"))


def icon(name):
    paths = {
        "image": '<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/>',
        "history": '<path d="M3 11a9 9 0 1 1 2.5 7.2M3 5v6h6M12 7v5l3 2"/>',
    }
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'


def navigate(route):
    st.session_state.route = route


def reset_case():
    st.session_state.upload_generation += 1
    st.session_state.description = ""
    st.session_state.confirmed = False
    st.session_state._description = ""
    st.session_state._confirmed = False
    st.session_state.evidence = None
    st.session_state.active_result = None


def sync_image():
    upload = st.session_state.get(f"image_{st.session_state.upload_generation}")
    st.session_state.evidence = {"content": upload.getvalue(), "name": upload.name} if upload else None
    st.session_state.confirmed = False
    st.session_state._confirmed = False


def sync_description():
    st.session_state.description = st.session_state._description
    st.session_state.confirmed = False
    st.session_state._confirmed = False


def sync_confirmation():
    st.session_state.confirmed = st.session_state._confirmed


def steps(image_ready, text_ready, result_ready):
    done = [image_ready and text_ready, result_ready, result_ready]
    current = 2 if result_ready else 1 if done[0] else 0
    parts = []
    for index, name in enumerate(["Prepara las señales", "Analiza", "Revisa el resultado"]):
        state = "done" if done[index] and index < current else "current" if index == current else ""
        parts.append(f'<div class="step {state}"><b>{index + 1}</b><span>{name}</span></div>')
    st.markdown('<div class="steps" aria-label="Etapas del análisis">' + '<div class="step-connector"></div>'.join(parts) + '</div>', unsafe_allow_html=True)


def sidebar():
    with st.sidebar:
        logo = (LOCAL / "assets/logo.svg").read_text(encoding="utf-8")
        st.markdown(f'<div class="brand">{logo}<div class="brand-name">Ojo<span>Alerta</span></div></div><div class="brand-caption">Cada señal cuenta.</div>', unsafe_allow_html=True)
        with st.container(key="navigation"):
            st.radio("Navegación", ["Analizar incidente", "Historial", "Cómo funciona"], key="route", label_visibility="collapsed")
        st.markdown('<div class="sidebar-label">CATEGORÍAS DEL MODELO</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-taxonomy">' + ''.join(f'<div class="taxonomy-item"><code>{code}</code><span>{label}</span></div>' for code, label in T.items()) + '</div>', unsafe_allow_html=True)
        st.divider()
        st.markdown('<div class="sidebar-note"><strong>Dos perspectivas, un análisis.</strong><br>Una imagen y una descripción del mismo incidente.</div>', unsafe_allow_html=True)
        st.caption(f"{len(st.session_state.history)} análisis en esta sesión · máximo {HISTORY_LIMIT}")
        with st.expander("Estado de los modelos"):
            for label, folder in [("Modelo de imagen", "01_visual/modelos/visual_spark_pipeline"), ("Modelo de texto", "02_textual/modelos/text_spark_pipeline")]:
                present = (ROOT / folder / "metadata").is_dir()
                st.write(f"**{label}** · {'Archivos encontrados' if present else 'Faltan archivos'}")
            st.caption("La carga real de los modelos se comprueba al analizar. El primer análisis puede tardar más.")
        st.markdown('<div class="sidebar-note">Prototipo académico<br>CLIP + Spark ML</div>', unsafe_allow_html=True)


def chart(result, comparison):
    table = result_table(result).sort_values("Combinación 50/50", ascending=False)
    labels = [f"{row['Categoría']} · {row['Código']}" for _, row in table.iterrows()]
    figure = go.Figure()
    if comparison:
        for column, color, name in [("Imagen", "#BC4535", "Imagen"), ("Texto", "#527E8C", "Texto"), ("Combinación 50/50", "#172B38", "Combinación")]:
            figure.add_trace(go.Bar(x=table[column], y=labels, orientation="h", name=name, marker_color=color, hovertemplate="%{y}<br>" + name + ": %{x:.1%}<extra></extra>"))
    else:
        figure.add_trace(go.Bar(x=table["Combinación 50/50"], y=labels, orientation="h", marker_color=["#BC4535"] + ["#A7BBC5"] * 3, text=[f"{p:.1%}" for p in table["Combinación 50/50"]], textposition="outside", cliponaxis=False, hovertemplate="%{y}<br>Probabilidad: %{x:.1%}<extra></extra>"))
    figure.update_layout(
        height=345 if comparison else 285, margin=dict(l=0, r=48, t=12, b=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope, sans-serif", size=12, color="#405461"),
        barmode="group", bargap=.35 if comparison else .48,
        legend=dict(orientation="h", y=1.18, x=0, title=None),
        xaxis=dict(range=[0, 1], tickformat=".0%", dtick=.25, showgrid=True, gridcolor="#E1E7EB", zeroline=False, fixedrange=True, title=None),
        yaxis=dict(autorange="reversed", showgrid=False, fixedrange=True, title=None),
        transition=dict(duration=0),
    )
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False, "responsive": True}, key="chart_" + ("compare_" if comparison else "fusion_") + result["id"])


def render_result(result, prefix="active"):
    code = result["category"]
    probability = max(result["fusion"])
    st.markdown(f'<div class="result-banner"><div class="result-title"><div><span class="result-code">{code} · Categoría estimada</span><h2>{T[code]}</h2></div><div class="result-value">{probability:.1%}<small>probabilidad combinada</small></div></div><p>Imagen y texto, con el mismo peso. Revisa también las categorías alternativas.</p></div>', unsafe_allow_html=True)
    visual_code, text_code = ORDEN[int(np.argmax(result["visual"]))], ORDEN[int(np.argmax(result["textual"]))]
    if visual_code != text_code:
        st.warning(f"Las señales difieren: la imagen prioriza {T[visual_code].lower()} y el texto, {T[text_code].lower()}. Revisa ambas entradas antes de interpretar la combinación.", icon=":material/compare_arrows:")
    else:
        st.caption(f"Ambos modelos priorizan {T[code].lower()}. Esta coincidencia no garantiza que la clasificación sea correcta.")
    view = st.segmented_control("Vista de probabilidades", ["Combinación", "Comparar modelos", "Tabla"], default="Combinación", key=prefix + "_view", label_visibility="collapsed")
    if view == "Tabla":
        display = result_table(result).copy()
        for column in ["Imagen", "Texto", "Combinación 50/50"]:
            display[column] = display[column].map(lambda p: f"{p:.1%}")
        st.dataframe(display, hide_index=True, use_container_width=True)
    else:
        chart(result, comparison=view == "Comparar modelos")
    st.caption("Las probabilidades son salidas de los modelos, no medidas de gravedad ni certezas jurídicas.")
    col_json, col_csv = st.columns(2)
    with col_json:
        st.download_button("Descargar informe JSON", export_json(result), file_name=f"ojoalerta_{result['id'][:8]}.json", mime="application/json", icon=":material/download:", use_container_width=True, key=prefix + "_json")
    with col_csv:
        st.download_button("Descargar probabilidades CSV", result_csv(result), file_name=f"ojoalerta_{result['id'][:8]}.csv", mime="text/csv", icon=":material/table_view:", use_container_width=True, key=prefix + "_csv")
    with st.expander("Detalle del análisis y sus límites"):
        st.write(f"**Imagen:** {result['filename']}")
        st.write(f"**Descripción analizada:** {result['description']}")
        st.caption(f"{result['created_at']} · procesamiento: {result['elapsed']:.2f} s")
        st.write("T01 (agresión) y T06 (disparos) se obtienen por correspondencias semánticas con las clases textuales de entrenamiento; no son equivalencias verificadas. La ponderación 50/50 es demostrativa y no se optimizó con incidentes pareados.")


def analyze():
    st.title("Analizar un incidente")
    st.markdown('<p class="intro">Conecta lo que ves con lo que describes. Añade las dos señales y explora cómo las interpretan los modelos.</p>', unsafe_allow_html=True)
    uploader_key = f"image_{st.session_state.upload_generation}"
    evidence = st.session_state.evidence
    previous_text = st.session_state.description.strip()
    active = st.session_state.active_result
    current_id = fingerprint(evidence["content"], previous_text) if evidence and previous_text else None
    steps(evidence is not None, bool(previous_text), bool(active and active["id"] == current_id))
    if "_description" not in st.session_state:
        st.session_state._description = st.session_state.description
    if "_confirmed" not in st.session_state:
        st.session_state._confirmed = st.session_state.confirmed
    image_col, text_col = st.columns([1, 1], gap="medium")
    image = None
    image_error = None
    with image_col, st.container(key="evidence"):
        st.markdown('<div class="work-heading"><h2>La imagen</h2><span class="step-label">Señal visual</span></div><p class="hint">Un fotograma que muestre el incidente.</p>', unsafe_allow_html=True)
        st.file_uploader("Imagen del incidente", type=["png", "jpg", "jpeg"], key=uploader_key, label_visibility="collapsed", on_change=sync_image)
        if evidence:
            try:
                image = decode_image(evidence["content"])
                st.image(image, use_container_width=True)
                st.caption(f"{evidence['name']} · {image.width:,} × {image.height:,} px · {len(evidence['content']) / 1024:.0f} KB")
            except ValueError as error:
                image_error = str(error)
                st.error(image_error)
        else:
            st.markdown(f'<div class="media-empty">{icon("image")}<strong>Aquí verás tu imagen</strong><p>Revisa que se distinga lo que quieres describir.</p></div>', unsafe_allow_html=True)
        st.markdown('<p class="description-tip">Usa una sola imagen, sin recortes que oculten el contexto.</p>', unsafe_allow_html=True)
    with text_col, st.container(key="narrative"):
        st.markdown('<div class="work-heading"><h2>La descripción</h2><span class="step-label">Señal textual</span></div><p class="hint">Cuenta qué sucede en esa misma imagen.</p>', unsafe_allow_html=True)
        description = st.text_area("Descripción del mismo incidente", key="_description", height=235, max_chars=MAX_DESCRIPTION, label_visibility="collapsed", placeholder="Describe las acciones que se observan, los objetos y el contexto de la escena…", on_change=sync_description)
        st.markdown(f'<div class="counter">{len(description):,} / {MAX_DESCRIPTION:,} caracteres</div>', unsafe_allow_html=True)
        st.markdown('<p class="description-tip"><strong>Una descripción útil:</strong> qué ocurre, qué elementos se observan y dónde sucede. Evita suposiciones que la imagen no permita comprobar.</p>', unsafe_allow_html=True)
    with st.container(key="analysis_actions"):
        st.markdown('<div class="analysis-footer"></div>', unsafe_allow_html=True)
        confirmed = st.checkbox("Confirmo que la imagen y la descripción corresponden al mismo incidente.", key="_confirmed", on_change=sync_confirmation)
        ready = image is not None and bool(description.strip()) and confirmed
        action, reset = st.columns([2.3, 1])
        with action:
            execute = st.button("Analizar incidente", type="primary", icon=":material/arrow_forward:", use_container_width=True)
        with reset:
            st.button("Limpiar entradas", icon=":material/restart_alt:", on_click=reset_case, use_container_width=True)
        status_text = "Todo listo para analizar" if ready else "Añade una imagen, escribe una descripción y confirma que corresponden."
        st.markdown(f'<div class="input-status {"ready" if ready else ""}" role="status"><span class="status-dot"></span>{status_text}</div>', unsafe_allow_html=True)
    if execute:
        if evidence is None:
            st.error("Añade una imagen JPG o PNG para continuar.")
        elif image_error:
            st.error("Reemplaza la imagen por un archivo válido antes de analizar.")
        elif not description.strip():
            st.error("Escribe qué sucede en la imagen para completar el análisis.")
        elif not confirmed:
            st.error("Confirma que ambas señales corresponden al mismo incidente.")
        else:
            st.session_state.active_result = None
            status = st.status("Analizando las dos señales…", expanded=True)
            try:
                with status:
                    st.write("Preparando la imagen y el texto. La primera carga puede tardar unos minutos.")
                    start = time.perf_counter()
                    visual, textual, _ = predecir(image, description.strip())
                    result = build_result(evidence["content"], description, evidence["name"], visual, textual, time.perf_counter() - start)
                    st.session_state.active_result = result
                    st.session_state.history = add_to_history(st.session_state.history, result)
                    status.update(label="Análisis completado", state="complete", expanded=False)
                st.rerun()
            except Exception as error:
                LOGGER.exception("No se pudo completar la inferencia")
                status.update(label="El análisis no pudo completarse", state="error", expanded=False)
                if isinstance(error, ModuleNotFoundError):
                    st.error("Falta una dependencia para ejecutar los modelos. Instala requirements.txt y vuelve a intentarlo. Encontrarás los pasos en «Cómo funciona».")
                elif isinstance(error, FileNotFoundError):
                    st.error("No se encontraron todos los archivos del modelo. Comprueba las carpetas de modelos en «Cómo funciona».")
                else:
                    st.error("No se pudieron cargar o ejecutar los modelos. Comprueba Java 17 o posterior, las dependencias y la conexión para la primera descarga de CLIP; después vuelve a intentarlo.")
                with st.expander("Detalle para resolver el problema"):
                    st.code(str(error), language=None)
    active = st.session_state.active_result
    current_id = fingerprint(evidence["content"], description) if evidence and description.strip() else None
    if active and active["id"] == current_id:
        st.divider()
        st.subheader("Lectura conjunta")
        render_result(active)
    elif active:
        st.info("Las entradas cambiaron. Vuelve a analizar para obtener un resultado de este caso. El análisis anterior sigue en el historial.", icon=":material/update:")
    else:
        st.markdown('<div class="method-strip"><strong>Dos señales que se complementan</strong><span>Imagen 50 %</span><div class="weight-track" aria-hidden="true"><i></i></div><span>Texto 50 %</span></div>', unsafe_allow_html=True)
        st.caption("La clasificación aparecerá aquí, con las cuatro categorías y una comparación de los modelos.")


def history():
    st.title("Historial de la sesión")
    st.markdown('<p class="intro">Vuelve a tus análisis, compara las señales y descarga los resultados que quieras conservar.</p>', unsafe_allow_html=True)
    records = st.session_state.history
    if not records:
        st.markdown(f'<div class="page-empty">{icon("history")}<h2>Tu primera lectura empieza aquí</h2><p>Los incidentes que analices aparecerán en este espacio. Añade una imagen y una descripción para comenzar.</p></div>', unsafe_allow_html=True)
        st.button("Analizar mi primer incidente", type="primary", icon=":material/arrow_forward:", on_click=navigate, args=("Analizar incidente",))
        return
    search_col, category_col = st.columns([2, 1])
    with search_col:
        query = st.text_input("Buscar en el historial", placeholder="Nombre de archivo o descripción", key="history_query")
    with category_col:
        category = st.selectbox("Categoría estimada", ["Todas"] + ORDEN, format_func=lambda value: value if value == "Todas" else f"{value} · {T[value]}")
    filtered = [record for record in records if (category == "Todas" or record["category"] == category) and query.casefold() in (record["filename"] + " " + record["description"]).casefold()]
    st.caption(f"{len(filtered)} de {len(records)} análisis · horarios de Perú (UTC−5)")
    if filtered:
        selected = st.selectbox("Abrir análisis", range(len(filtered)), format_func=lambda index: f"{filtered[index]['created_at'][11:16]} · {filtered[index]['filename']} · {T[filtered[index]['category']]}", key="history_selected")
        result = filtered[selected]
        left, right = st.columns([1, 1.8], gap="large")
        with left:
            st.image(result["thumbnail"], use_container_width=True)
            st.write(result["description"])
        with right:
            render_result(result, prefix="history")
    else:
        st.info("No hay análisis que coincidan con estos filtros. Prueba otra búsqueda o selecciona «Todas».")
    st.divider()
    export_col, clear_col = st.columns([2, 1])
    with export_col:
        report = json.dumps([json.loads(export_json(record)) for record in records], ensure_ascii=False, indent=2)
        st.download_button("Exportar toda la sesión (JSON)", report, file_name="ojoalerta_sesion.json", mime="application/json", icon=":material/download:")
    with clear_col:
        st.button("Vaciar historial", icon=":material/delete_outline:", on_click=lambda: st.session_state.update(history=[]))
    st.caption(f"Se conservan hasta {HISTORY_LIMIT} casos en la memoria de esta sesión. Al cerrarla o reiniciar el servidor, pueden perderse; descarga los informes para conservarlos.")


def guide():
    st.title("Cómo funciona OjoAlerta")
    st.markdown('<p class="intro">Una lectura de la imagen y otra del texto. La combinación reúne ambas perspectivas para explorar un mismo incidente.</p>', unsafe_allow_html=True)
    for heading, body in [
        ("Observa y describe", "Carga una imagen y describe lo que sucede en ella. Las dos entradas deben corresponder al mismo incidente; el sistema no comprueba por sí solo que coincidan."),
        ("Analiza las dos señales", "El modelo visual usa CLIP para extraer características de la imagen y Spark ML para clasificarla. El modelo textual procesa la descripción mediante tokenización, TF-IDF y regresión logística."),
        ("Combina y compara", "Cada modelo produce probabilidades. OjoAlerta calcula el promedio con un peso del 50 % para la imagen y del 50 % para el texto. En el resultado puedes ver la combinación, comparar los modelos o consultar la tabla."),
    ]:
        st.markdown(f'<div class="guide-row"><h3>{heading}</h3><p>{body}</p></div>', unsafe_allow_html=True)
    st.subheader("Qué significan las categorías")
    st.dataframe([
        {"Código": "T01", "Categoría": "Agresión", "Clases textuales agrupadas": "Homicidio, Lesiones"},
        {"Código": "T02", "Categoría": "Robo", "Clases textuales agrupadas": "Robo, Robo agravado"},
        {"Código": "T03", "Categoría": "Sustracción", "Clases textuales agrupadas": "Hurto"},
        {"Código": "T06", "Categoría": "Disparos", "Clases textuales agrupadas": "Tenencia ilegal de armas"},
    ], hide_index=True, use_container_width=True)
    st.caption("T01 y T06 son aproximaciones semánticas: las clases agrupadas no son equivalencias verificadas de las categorías visuales.")
    with st.expander("Cómo interpretar el resultado", expanded=True):
        st.write("La categoría estimada es la de mayor probabilidad combinada. Un porcentaje alto no es una medida de precisión del sistema. Si las señales difieren, revisa qué parte del contexto aporta cada una.")
        st.write("La ponderación 50/50 es demostrativa: no está optimizada con datos pareados. Esta interfaz no reentrena los modelos ni calcula nuevas métricas de evaluación.")
    with st.expander("Preparar los modelos y ejecutar el proyecto"):
        st.write("Usa Python 3.10 o posterior y Java 17 o posterior. Conserva completas las carpetas de modelos, incluidos sus archivos .parquet.")
        st.code("python -m pip install -r requirements.txt\npython comprobar_modelos.py\npython -m streamlit run app.py", language="bash")
        st.write("La primera ejecución descarga CLIP si no está en 01_visual/modelos/clip_preentrenado o en la caché. Las siguientes reutilizan los recursos cargados. OJOALERTA_ROOT permite indicar otra carpeta para los modelos.")
    with st.expander("Qué se conserva en la sesión"):
        st.write(f"El historial mantiene hasta {HISTORY_LIMIT} casos con una miniatura, la descripción y las probabilidades. No crea una base de datos ni guarda informes automáticamente en disco. Los datos se procesan en el servidor donde ejecutes la aplicación.")
    st.button("Volver al análisis", type="primary", icon=":material/arrow_forward:", on_click=navigate, args=("Analizar incidente",))


def main():
    st.set_page_config(page_title="OjoAlerta · Analiza un incidente", page_icon=":material/visibility:", layout="wide")
    defaults = {"route": "Analizar incidente", "history": [], "active_result": None, "upload_generation": 0, "description": "", "confirmed": False, "evidence": None}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    css = (LOCAL / "assets/styles.css").read_text(encoding="utf-8")
    font = (LOCAL / "assets/Manrope-Variable.ttf").read_bytes()
    st.markdown(f"<style>{stylesheet(css, font)}</style>", unsafe_allow_html=True)
    sidebar()
    st.markdown('<div class="app-topline"><span>Espacio de análisis de incidentes</span><span class="pill"><i></i>Prototipo académico</span></div>', unsafe_allow_html=True)
    pages = {"Analizar incidente": analyze, "Historial": history, "Cómo funciona": guide}
    with st.container(key=f"page-{list(pages).index(st.session_state.route)}"):
        pages[st.session_state.route]()
    st.markdown('<div class="footer"><span><strong>OjoAlerta</strong> · Cada señal cuenta.</span><span>Uso académico. No utilizar para decisiones reales de seguridad ni identificación de responsables.</span></div>', unsafe_allow_html=True)
