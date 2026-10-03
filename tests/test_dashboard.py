from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "dashboard/app.py"


def test_dashboard_navigation_and_missing_denominator_behavior():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    assert not app.exception
    assert len(app.metric) == 3
    for section in ["Territorios", "Laboratorio", "Tendencias", "Europa", "Modelos", "Fuentes"]:
        app.radio(key="section").set_value(section).run()
        assert not app.exception, section
    app.radio(key="section").set_value("Territorios").run()
    app.selectbox(key="year").set_value(2023).run()
    app.selectbox(key="denominator").set_value("registered_vehicles").run()
    assert not app.exception
    assert any("52 provincias" in warning.value for warning in app.warning)


def test_laboratory_zero_weights_is_a_clear_validation_state():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    app.radio(key="section").set_value("Laboratorio").run()
    for i in range(4):
        app.slider(key=f"weight_{i}").set_value(0.0)
    app.run()
    assert not app.exception
    assert any("mayor que cero" in warning.value for warning in app.warning)
