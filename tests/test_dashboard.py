from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "dashboard/app.py"


def test_research_dashboard_navigation_and_observed_denominators():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    assert not app.exception
    assert len(app.metric) == 3
    for section in [
        "Golpes de chapa",
        "Territorios",
        "Laboratorio",
        "Tendencias",
        "Europa",
        "Modelos",
        "Fuentes",
    ]:
        app.radio(key="section").set_value(section).run()
        assert not app.exception, section
    app.radio(key="section").set_value("Territorios").run()
    app.selectbox(key="year").set_value(2023).run()
    app.selectbox(key="denominator").set_value("registered_vehicles").run()
    assert not app.exception
    assert not any("52 provincias" in warning.value for warning in app.warning)


def test_laboratory_zero_weights_is_a_clear_validation_state():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    app.radio(key="section").set_value("Laboratorio").run()
    for i in range(4):
        app.slider(key=f"weight_{i}").set_value(0.0)
    app.run()
    assert not app.exception
    assert any("mayor que cero" in warning.value for warning in app.warning)


def test_insurance_access_filters_and_fixed_year_scope():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    app.button(key="open_insurance").click().run()
    assert not app.exception
    assert app.radio(key="section").value == "Golpes de chapa"
    assert app.selectbox(key="insurance_coverage").value == "rc_material"
    assert "year" not in [widget.key for widget in app.selectbox]
    assert app.metric[0].value == "15,85 %"
    assert len(app.dataframe[0].value) == 20
    assert "Melilla" in app.dataframe[0].value["Ciudad"].tolist()
    app.selectbox(key="insurance_selection").set_value("lower").run()
    assert not app.exception
    assert "Orihuela" in app.dataframe[0].value["Ciudad"].tolist()
    app.selectbox(key="insurance_selection").set_value("both").run()
    assert len(app.dataframe[0].value) == 40
    app.selectbox(key="insurance_coverage").set_value("rc_corporal").run()
    assert not app.exception
    assert "Chiclana de la Fron." in app.dataframe[0].value["Ciudad"].tolist()
