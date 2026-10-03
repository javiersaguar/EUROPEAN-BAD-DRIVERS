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
st.set_option("client.toolbarMode", "minimal")
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
        [
            "Panorama",
            "Golpes de chapa",
            "Territorios",
            "Laboratorio",
            "Tendencias",
            "Europa",
            "Modelos",
            "Fuentes",
        ],
        key="section",
    )
    if section == "Golpes de chapa":
        year = 2024
        st.caption("Seguros · datos de 2024\n\nUNESPA · publicación: febrero de 2026")
    else:
        year = st.selectbox("Año", sorted(panel.year.unique(), reverse=True), key="year")
    st.divider()
    if section != "Golpes de chapa":
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
st.title("Golpes de chapa" if section == "Golpes de chapa" else "¿Dónde cambia la siniestralidad?")
scope_note = (
    "Daños materiales registrados por el seguro · UNESPA, 2024. Los partes de responsabilidad civil material permiten explorar los golpes de chapa; un mismo accidente puede generar también daños corporales."
    if section == "Golpes de chapa"
    else "Medimos siniestralidad registrada y carga territorial. La población, el parque y los permisos son aproximaciones a la exposición; este índice no mide la capacidad de conducir de las personas."
)
st.markdown(
    f'<div class="note">{scope_note}</div>',
    unsafe_allow_html=True,
)

if section == "Panorama":
    st.button(
        "Ver datos de golpes de chapa →",
        on_click=lambda: st.session_state.update(section="Golpes de chapa"),
        key="open_insurance",
    )
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

elif section == "Golpes de chapa":
    insurance_path = ROOT / "outputs/tables/insurance_coverage.csv"
    if not insurance_path.exists():
        st.info(
            "Faltan las tablas de seguros. Ejecuta `uv run ebdi download` y `uv run ebdi insurance`."
        )
        st.stop()
    coverages = load_table("insurance_coverage")
    municipal = load_table("insurance_municipal")
    quality = json.loads(
        (ROOT / "outputs/tables/insurance_quality.json").read_text(encoding="utf-8")
    )
    material = coverages.loc[coverages.coverage.eq("Resp. civil material")].iloc[0]
    cols = st.columns(3)
    cols[0].metric(
        "Partes de RC material / total", f"{material.claims_share_pct:.2f}".replace(".", ",") + " %"
    )
    cols[1].metric(
        "Coste medio de RC material", f"{int(material.mean_cost_eur):,}".replace(",", ".") + " €"
    )
    cols[2].metric("Ciudades publicadas · RC material", "40")
    st.caption(
        "España, 2024 · cuota de partes por cobertura y coste por parte; no son probabilidades de accidente."
    )
    st.subheader("Daños materiales por ciudad")
    st.write(
        "Ciudades de más de 50.000 habitantes: el informe publica las 20 diferencias más altas y las 20 más bajas frente a la referencia nacional."
    )
    c1, c2 = st.columns(2)
    coverage_code = c1.selectbox(
        "Cobertura aseguradora",
        ["rc_material", "rc_corporal"],
        format_func={
            "rc_material": "Daños materiales · golpes de chapa",
            "rc_corporal": "Daños corporales · comparación",
        }.get,
        key="insurance_coverage",
    )
    selection = c2.selectbox(
        "Ciudades publicadas",
        ["higher", "lower", "both"],
        format_func={
            "higher": "20 por encima de la referencia",
            "lower": "20 por debajo de la referencia",
            "both": "Las 40 ciudades publicadas",
        }.get,
        key="insurance_selection",
    )
    selected = municipal.loc[municipal.coverage.eq(coverage_code)].copy()
    if selection != "both":
        selected = selected.loc[selected.selection.eq(selection)]
    selected = selected.sort_values("relative_difference_pct")
    selected["Diferencia"] = selected.selection.map({"higher": "Por encima", "lower": "Por debajo"})
    fig = px.bar(
        selected,
        x="relative_difference_pct",
        y="municipality",
        orientation="h",
        color="Diferencia",
        color_discrete_map={"Por encima": "#cd693e", "Por debajo": "#163b4c"},
        hover_data=["province_source", "year"],
        text="relative_difference_pct",
        labels={
            "relative_difference_pct": "Diferencia relativa frente a la referencia nacional (%)",
            "municipality": "Ciudad",
            "province_source": "Provincia",
        },
    )
    fig.update_traces(texttemplate="%{x:+.2f}%", textposition="outside", cliponaxis=False)
    fig.update_layout(height=max(580, len(selected) * 25 + 100), showlegend=False, yaxis_title=None)
    fig.add_vline(x=0, line_color="#55717d", line_width=1)
    fig.update_xaxes(
        range=[
            min(0, selected.relative_difference_pct.min()) * 1.25,
            max(0, selected.relative_difference_pct.max()) * 1.25,
        ]
    )
    st.plotly_chart(style(fig), width="stretch", key="insurance_cities")
    st.caption(
        "Ejemplo: +40,99 % expresa una diferencia relativa frente a la referencia, no un 40,99 % de probabilidad de accidente. No se publican recuentos ni vehículos-año asegurados por ciudad; las ciudades ausentes no se imputan."
    )
    st.dataframe(
        selected[
            ["municipality", "province_source", "relative_difference_pct", "source_page"]
        ].rename(
            columns={
                "municipality": "Ciudad",
                "province_source": "Provincia",
                "relative_difference_pct": "Diferencia relativa (%)",
                "source_page": "Página del informe",
            }
        ),
        hide_index=True,
        width="stretch",
    )
    export(selected.drop(columns="Diferencia"), f"seguros_2024_{coverage_code}_{selection}")
    with st.expander("Daños propios, lunas y otras coberturas · España"):
        st.dataframe(
            coverages[
                ["coverage", "claims_share_pct", "payments_share_pct", "mean_cost_eur"]
            ].rename(
                columns={
                    "coverage": "Cobertura",
                    "claims_share_pct": "Partes / total (%)",
                    "payments_share_pct": "Pagos / total (%)",
                    "mean_cost_eur": "Coste medio (€)",
                }
            ),
            hide_index=True,
            width="stretch",
        )
        st.caption(
            "Porcentajes redondeados por el editor. Daños propios incluye más casos que colisiones; lunas también puede incluir roturas sin accidente. No se convierten las cuotas en recuentos exactos."
        )
        export(coverages, "seguros_2024_coberturas")
    with st.expander("Volumen provincial · todas las coberturas del seguro"):
        provinces = load_table("insurance_provinces")
        st.write(
            "Estos recuentos incluyen asistencia en carretera, robos y otras coberturas: no son un total de golpes de chapa ni de accidentes únicos."
        )
        st.dataframe(provinces, hide_index=True, width="stretch")
        st.caption(
            "50 provincias publicadas; Ceuta y Melilla no aparecen en esta tabla. La suma provincial es inferior al total nacional en 17.707 partes y 24.573.178 €. Conservamos la diferencia del informe sin repartirla entre territorios."
        )
        export(provinces, "seguros_2024_todas_coberturas_provincias")
    st.markdown(
        f"Fuente: [UNESPA · informe oficial de siniestros de automóvil 2024]({quality['source_url']}), tablas 1, 2, 8 y 9. Elaboración del editor con MicroESA y FIVA."
    )
    st.caption(
        "La fuente no identifica un total exhaustivo de accidentes sin lesiones. Estos datos aseguradores se muestran con sus propias definiciones y no entran en el índice de DGT."
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
            "El archivo histórico de Insurance Europe termina en 2016 y sus tablas de frecuencia admiten varios denominadores. La sección Golpes de chapa sí ofrece datos UNESPA de 2024 para ciudades españolas seleccionadas, pero faltan recuentos y vehículos-año por cobertura para un panel comparable entre países."
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
        ("Daños materiales y seguros", "insurance.md"),
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
    "EBDI · Datos: DGT, INE, Eurostat / CARE, UNESPA · Valores experimentales, no juicios sobre personas ni territorios."
)
