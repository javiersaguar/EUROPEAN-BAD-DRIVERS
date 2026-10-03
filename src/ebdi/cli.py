"""Cross-platform entry point for every reproducible project stage."""

import argparse
from pathlib import Path

from ebdi.utils.io import project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="European Bad Drivers Index research pipeline")
    parser.add_argument(
        "command",
        choices=["download", "process", "analysis", "model", "explain", "all", "dashboard"],
    )
    parser.add_argument("--root", type=Path)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Cache a new publisher revision without overwriting raw files",
    )
    args = parser.parse_args()
    root = args.root.resolve() if args.root else project_root()
    if args.command in {"download", "all"}:
        from ebdi.ingestion.download import download

        download(root, args.refresh)
    if args.command in {"process", "all"}:
        from ebdi.cleaning.pipeline import process

        print(process(root))
    if args.command in {"analysis", "all"}:
        from ebdi.visualization.reports import analysis

        analysis(root)
    if args.command in {"model", "all"}:
        from ebdi.modeling.severity import train

        train(root)
    if args.command == "explain":
        from ebdi.modeling.explain import explain

        explain(root)
    if args.command == "dashboard":
        import subprocess
        import sys

        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(root / "dashboard/app.py")],
            cwd=root,
            check=True,
        )


if __name__ == "__main__":
    main()
