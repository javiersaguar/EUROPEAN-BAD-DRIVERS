"""Spanish dashboard; aggregated published results work without raw source files."""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from ebdi.metrics.index import METHODS, composite, validate_weights
from ebdi.metrics.rates import DENOMINATORS, INCIDENTS
from ebdi.utils.io import read_yaml
from ebdi.visualization.charts import choropleth, label, ranking, style

ROOT = Path(__file__).resolve().parents[1]
st.set_page_config(page_title="EBDI · Observatorio vial", page_icon="🚦", layout="wide")
st.markdown(
    """<style>
.block-container {max-width: 1400px; padding-top: 4rem;}
h1 {font-weight: 650; letter-spacing: -0.035em;}
h2 {letter-spacing: -0.02em;}
[data-testid="stMetric"] {border-top: 2px solid #163b4c; padding-top: 14px;}
.eyebrow {font-size: 12px; letter-spacing: .16em; text-transform: uppercase; color: #55717d;}
.note {border-left: 3px solid #cd693e; padding: 10px 16px; background: #f7f0e5; margin: 14px 0 25px;}
</style>""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_table(name: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / "outputs/tables" / f"{name}.csv", dtype={"province_code": str})


def export(frame: pd.DataFrame, name: str) -> None:
    st.download_button(
        "Descargar tabla · CSV",
        frame.to_csv(index=False).encode("utf-8-sig"),
        f"{name}.csv",
        "text/csv",
        key=f"download_{name}",
    )


if not (ROOT / "outputs/tables/spain_metrics.csv").exists():
    st.error("Faltan resultados. Ejecuta `uv run ebdi all` desde el repositorio.")
    st.stop()

panel = load_table("spain_metrics")
config = read_yaml(ROOT / "configs/index_weights.yaml")
with st.sidebar:
    st.markdown("**EBDI** / Observatorio vial")
    st.caption("Datos oficiales · decisiones transparentes")
    section = st.radio(
        "Explorar",
        ["Panorama", "Territorios", "Laboratorio", "Tendencias", "Europa", "Modelos", "Fuentes"],
        key="section",
    )
    year = st.selectbox("Año", sorted(panel.year.unique(), reverse=True), key="year")
    st.divider()
    st.caption("España · 52 provincias\n\nDGT + INE · 2022–2024")
    st.caption("Autor: Javier Saguar")
    st.link_button(
        "Repositorio y metodología", "https://github.com/javiersaguar/EUROPEAN-BAD-DRIVERS"
    )

current = panel.loc[panel.year.eq(year)].copy()
st.markdown(
    '<div class="eyebrow">European Bad Drivers Index / Laboratorio de datos</div>',
    unsafe_allow_html=True,
)
st.title("¿Dónde cambia la siniestralidad?")
st.markdown(
    '<div class="note">Medimos siniestralidad registrada y carga territorial. La población, el parque y los permisos son aproximaciones a la exposición; este índice no mide la capacidad de conducir de las personas.</div>',
    unsafe_allow_html=True,
)

if section == "Panorama":
    st.subheader(f"España, {year} · tres cifras, tres preguntas")
    cols = st.columns(3)
    cols[0].metric("Siniestros con víctimas", f"{int(current.injury_crashes.sum()):,}")
    cols[1].metric("Fallecidos a 30 días", f"{int(current.fatalities.sum()):,}")
    cols[2].metric(
        "Siniestros / 100.000 habitantes",
        f"{current.injury_crashes.sum() / current.population.sum() * 100_000:.1f}",
    )
    st.caption(
        "Numeradores: DGT. Población: INE 67988, a 1 de enero del mismo año. Los fallecidos incluyen a todos los usuarios de la vía."
    )
    st.subheader("La respuesta depende de lo que midas")
    left, right = st.columns(2)
    left.plotly_chart(
        ranking(current, "injury_crashes_per_100k_population", 10),
        width="stretch",
        key="overview_injury",
    )
    right.plotly_chart(
        ranking(current, "fatalities_per_100k_population", 10),
        width="stretch",
        key="overview_fatal",
    )
    st.caption(
        "Barras: tasas observadas. Intervalos: modelo Poisson al 95%, condicionado al denominador; no incluyen sesgo de notificación ni movilidad real."
    )
    correlation = (
        current[["injury_crashes_per_100k_population", "fatalities_per_100k_population"]]
        .corr(method="spearman")
        .iloc[0, 1]
    )
    st.info(
        f"En {year}, la correlación de rankings entre tasas de siniestros y mortalidad es {correlation:.3f}. Elegir un indicador cambia la pregunta que responde el ranking."
    )
    breakdown_path = ROOT / "outputs/tables/crash_breakdowns.csv"
    if breakdown_path.exists():
        with st.expander("Cuándo y cómo se registran los siniestros"):
            groups = load_table("crash_breakdowns")
            dimension = st.selectbox(
                "Dimensión",
                ["MES", "HORA", "DIA_SEMANA", "TIPO_ACCIDENTE", "TIPO_VIA", "CONDICION_METEO"],
                key="eda_dimension",
            )
            grouped = groups.loc[groups.year.eq(year) & groups.dimension.eq(dimension)]
            fig = px.bar(
                grouped,
                x="label",
                y="injury_crashes",
                hover_data=["severe_crashes", "conditional_severe_fraction", "small_sample"],
                labels={
                    "label": "Categoría registrada",
                    "injury_crashes": "Siniestros registrados",
                },
            )
            st.plotly_chart(style(fig), width="stretch", key="eda_counts")
            st.caption(
                "Recuentos y gravedad entre siniestros registrados. Sin viajes o kilómetros por grupo, no miden la probabilidad de sufrir un accidente."
            )

elif section == "Territorios":
    st.subheader("Un territorio, varios denominadores")
    c1, c2 = st.columns(2)
    incident = c1.selectbox("Indicador", list(INCIDENTS), format_func=INCIDENTS.get, key="incident")
    denominator = c2.selectbox(
        "Denominador", list(DENOMINATORS), format_func=DENOMINATORS.get, key="denominator"
    )
    raw = st.checkbox("Mostrar también recuentos sin normalizar", key="raw")
    metric = f"{incident}_per_100k_{denominator}"
    st.caption(label(metric))
    missing = int(current[metric].isna().sum())
    if missing:
        st.warning(
            f"{missing} provincias sin este denominador para {year}. Quedan fuera del ranking; no se interpolan ni se sustituyen por cero."
        )
    else:
        geometry_path = ROOT / "data/processed/spain_provinces.geojson"
        if geometry_path.exists():
            geo = json.loads(geometry_path.read_text(encoding="utf-8"))
            st.plotly_chart(choropleth(current, metric, geo), width="stretch", key="spain_map")
            st.caption(
                "Límites: © EuroGeographics; cartografía Eurostat/GISCO, NUTS 2024. Islas agregadas a provincia. Uso conforme a las condiciones GISCO."
            )
        else:
            st.info(
                "El mapa se genera al ejecutar `uv run ebdi download` y `uv run ebdi process`. Las tablas publicadas están disponibles aquí."
            )
        st.plotly_chart(ranking(current, metric), width="stretch", key="territory_rank")
    if raw:
        st.plotly_chart(ranking(current, incident), width="stretch", key="territory_raw")
        st.caption("Recuento de eventos, sin exposición: no es una tasa de riesgo.")
    if incident == "rear_lateral_crashes":
        st.caption(
            f"{int(current.unknown_collision.sum())} siniestros con tipo de colisión desconocido: no se asignan a alcance/lateral."
        )
    cols = [
        "province",
        "year",
        incident,
        denominator,
        metric,
        f"{metric}_lower",
        f"{metric}_upper",
        "unknown_collision",
        "small_sample",
    ]
    table = current[cols].sort_values(metric, ascending=False, na_position="last")
    st.dataframe(table, hide_index=True, width="stretch")
    export(table, f"territorios_{year}_{incident}_{denominator}")

elif section == "Laboratorio":
    st.subheader("Construye una definición y observa cómo cambia")
    st.caption(
        "Componentes solapados: siniestros con víctimas, urbanos, alcance/lateral y mortalidad, por población. Los pesos expresan decisiones del analista."
    )
    component_names = [
        "Siniestros con víctimas",
        "Siniestros urbanos",
        "Alcance / lateral",
        "Fallecidos",
    ]
    columns = st.columns(4)
    weights = {
        component: columns[i].slider(
            component_names[i], 0.0, 1.0, float(weight), 0.05, key=f"weight_{i}"
        )
        for i, (component, weight) in enumerate(config["weights"].items())
    }
    method = st.selectbox("Normalización dentro del año seleccionado", METHODS, key="normalization")
    if sum(weights.values()) == 0:
        st.warning("Elige al menos un peso mayor que cero para calcular el índice.")
    else:
        actual_weights = validate_weights(weights)
        result = composite(current, weights, method, config["minimum_injury_crashes"])
        baseline = composite(
            current, config["weights"], config["normalization"], config["minimum_injury_crashes"]
        )
        equal = composite(
            current, dict.fromkeys(config["weights"], 1.0), method, config["minimum_injury_crashes"]
        )
        result["default_rank"] = baseline.index_rank
        result["equal_weight_rank"] = equal.index_rank
        result["rank_change"] = result.index_rank - result.default_rank
        st.caption(
            "Pesos efectivos: "
            + " · ".join(
                f"{component_names[list(config['weights']).index(k)]} {v:.0%}"
                for k, v in actual_weights.items()
            )
        )
        if method in {"zscore", "robust_zscore"}:
            st.caption(
                "Escala estandarizada, sin límites 0–100. Los percentiles y min–max sí usan una escala 0–100."
            )
        fig = px.scatter(
            result,
            x="default_rank",
            y="index_rank",
            hover_name="province",
            color="rank_change",
            color_continuous_scale="RdBu",
            labels={"default_rank": "Ranking de referencia", "index_rank": "Ranking con tus pesos"},
        )
        fig.add_shape(
            type="line", x0=1, x1=52, y0=1, y1=52, line={"color": "#9eaaa9", "dash": "dot"}
        )
        st.plotly_chart(style(fig), width="stretch", key="rank_lab")
        st.dataframe(
            result[
                [
                    "province",
                    "injury_crashes",
                    "index_score",
                    "index_rank",
                    "default_rank",
                    "equal_weight_rank",
                    "rank_change",
                    "index_eligible",
                ]
            ].sort_values("index_rank"),
            hide_index=True,
            width="stretch",
        )
        export(result, f"index_{year}_{method}")
    if int(year) == int(panel.year.max()) and (ROOT / "outputs/tables/sensitivity.csv").exists():
        with st.expander("Sensibilidad publicada: 500 pesos alternativos y bootstrap"):
            st.dataframe(load_table("sensitivity"), hide_index=True, width="stretch")
            st.caption(
                "Los rangos de pesos describen decisiones metodológicas. Los intervalos bootstrap usan un modelo de repetición de eventos con denominadores fijos. Son conceptos diferentes y no cubren sesgo sistemático."
            )

elif section == "Tendencias":
    st.subheader("¿Se mantiene el patrón con el tiempo?")
    provinces = st.multiselect(
        "Provincias",
        sorted(panel.province.unique()),
        default=["Madrid", "Barcelona", "Zamora"],
        key="trend_provinces",
    )
    incident = st.selectbox(
        "Indicador temporal", list(INCIDENTS), format_func=INCIDENTS.get, key="trend_incident"
    )
    metric = f"{incident}_per_100k_population"
    if provinces:
        df = panel.loc[panel.province.isin(provinces)].sort_values("year")
        fig = px.line(
            df,
            x="year",
            y=metric,
            color="province",
            markers=True,
            hover_data=[incident, "population"],
            labels={metric: label(metric), "year": "Año", "province": "Provincia"},
        )
        fig.update_xaxes(dtick=1)
        st.plotly_chart(style(fig), width="stretch", key="trends")
    st.caption(
        "Tres años permiten una primera comparación, pero no una tendencia estructural ni causal. Se mantiene la definición del indicador y la población de 1 de enero."
    )
    if (ROOT / "outputs/tables/year_rank_stability.csv").exists():
        st.markdown("**Estabilidad del índice de referencia · correlación de rankings**")
        st.dataframe(load_table("year_rank_stability"), hide_index=True, width="stretch")

elif section == "Europa":
    st.subheader("Europa · una comparación que sí comparte definición")
    st.caption(
        "UE-27: fallecidos a 30 días por millón de habitantes. Eurostat / CARE y población a 1 de enero. No es una comparación de habilidad al volante."
    )
    euro = load_table("europe_metrics")
    euro = euro.loc[euro.year.eq(year)].sort_values("fatalities_per_million_population")
    fig = px.bar(
        euro,
        x="fatalities_per_million_population",
        y="country",
        orientation="h",
        color=euro.geo.eq("ES").map({True: "España", False: "UE"}),
        color_discrete_map={"España": "#cd693e", "UE": "#163b4c"},
        hover_data=["fatalities", "population", "fatalities_status", "population_status"],
    )
    fig.update_layout(
        height=850,
        showlegend=False,
        xaxis_title="Fallecidos por millón de habitantes",
        yaxis_title=None,
    )
    st.plotly_chart(style(fig), width="stretch", key="europe")
    st.dataframe(euro, hide_index=True, width="stretch")
    st.caption(
        "Las banderas de Eurostat se conservan: p provisional, e estimado, b ruptura de serie, d definición distinta (cuando existan). Los fallecidos son más comparables que las lesiones, aunque persisten diferencias de registro y seguimiento."
    )
    export(euro, f"europa_{year}")
    with st.expander("Por qué no añadimos un ranking europeo de golpes de chapa"):
        st.write(
            "El archivo histórico de Insurance Europe termina en 2016 y sus tablas de frecuencia admiten varios denominadores. Las unidades y notas de cada país necesitan validación. UNESPA no aporta aquí un panel provincial completo de siniestros y vehículos-año asegurados. Estas observaciones no se mezclan con los siniestros de DGT de 2022–2024."
        )

elif section == "Modelos":
    st.subheader("Gravedad condicionada a un siniestro registrado")
    st.info(
        "Objetivo: al menos un fallecido u hospitalizado en un siniestro con víctimas. No predice la probabilidad anual de que una persona tenga un accidente."
    )
    if (ROOT / "outputs/tables/model_metrics.csv").exists():
        st.caption(
            "Entrenamiento: 2022 · selección de modelo: 2023 · evaluación final: 2024. Se excluyen todos los totales de víctimas y variables derivadas del desenlace."
        )
        st.dataframe(load_table("model_metrics"), hide_index=True, width="stretch")
        if (ROOT / "outputs/tables/model_calibration.csv").exists():
            df = load_table("model_calibration")
            fig = px.line(
                df,
                x="mean_prediction",
                y="observed_frequency",
                color="model",
                markers=True,
                hover_data=["n"],
                labels={
                    "mean_prediction": "Frecuencia predicha",
                    "observed_frequency": "Frecuencia observada",
                },
            )
            fig.add_shape(
                type="line", x0=0, x1=1, y0=0, y1=1, line={"color": "#9eaaa9", "dash": "dot"}
            )
            st.plotly_chart(style(fig), width="stretch", key="calibration")
        if (ROOT / "outputs/tables/model_permutation_importance.csv").exists():
            st.markdown("**Asociación predictiva · importancia por permutación**")
            st.dataframe(
                load_table("model_permutation_importance"), hide_index=True, width="stretch"
            )
            st.caption(
                "La importancia refleja asociación y depende del modelo y sus correlaciones. No es un efecto causal."
            )
        shap_path = ROOT / "outputs/figures/model_shap_summary.png"
        if shap_path.exists():
            with st.expander("Cómo reparte el modelo sus predicciones · SHAP"):
                st.image(str(shap_path), width="stretch")
                st.dataframe(load_table("model_shap_importance"), hide_index=True, width="stretch")
                st.caption(
                    "400 siniestros de 2024, muestra reproducible. Atribuciones en log-odds: suman la diferencia respecto a la predicción de referencia. Variables correlacionadas y su codificación condicionan el reparto; no representa causalidad."
                )
    else:
        st.write(
            "El experimento se reproduce con `uv run ebdi model` después de procesar los datos. Se necesita el archivo local de siniestros; los resultados agregados no permiten entrenar un modelo individual."
        )

elif section == "Fuentes":
    st.subheader("Trazabilidad y límites, a la vista")
    sources = read_yaml(ROOT / "configs/sources.yaml")["sources"]
    st.dataframe(
        pd.DataFrame(
            [
                {
                    k: s[k]
                    for k in [
                        "id",
                        "organization",
                        "years",
                        "geographic_level",
                        "observation_unit",
                        "denominator",
                        "url",
                    ]
                }
                for s in sources
            ]
        ),
        hide_index=True,
        width="stretch",
    )
    for title, filename in [
        ("Metodología", "methodology.md"),
        ("Auditoría de viabilidad", "data_feasibility.md"),
        ("Calidad", "data_quality.md"),
        ("Limitaciones", "limitations.md"),
        ("Diccionario de datos", "data_dictionary.md"),
    ]:
        path = ROOT / "docs" / filename
        if path.exists():
            with st.expander(title):
                st.markdown(path.read_text(encoding="utf-8"))
    st.caption(
        "Código MIT · fuentes con sus propias condiciones de reutilización · auditoría del 3 de octubre de 2026."
    )

st.divider()
st.caption(
    "EBDI · Datos: DGT, INE, Eurostat / CARE · Valores experimentales, no juicios sobre personas ni territorios."
)
