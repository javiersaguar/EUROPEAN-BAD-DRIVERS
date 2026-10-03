import runpy
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/build_notebooks.py"
CONTENT = runpy.run_path(str(SCRIPT))


@pytest.mark.parametrize("book", CONTENT["BOOKS"])
def test_generated_notebook_code_is_valid_python(book):
    name, _, sections = book
    compile(CONTENT["SETUP"], f"{name}:setup", "exec")
    for title, source in sections:
        compile(source, f"{name}:{title}", "exec")
