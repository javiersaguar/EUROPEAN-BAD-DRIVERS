"""Cross-platform entry point for every reproducible project stage."""

import argparse
from pathlib import Path

from ebdi.utils.io import project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="European Bad Drivers Index research pipeline")
    parser.add_argument(
        "command",
        choices=[
            "download",
            "process",
            "insurance",
            "analysis",
            "model",
            "explain",
            "all",
            "dashboard",
            "history",
            "exposure",
            "alternative",
            "policy",
            "site",
            "monitor",
            "claims-import",
            "demographics",
            "material",
            "ncid",
            "extended-analysis",
        ],
    )
    parser.add_argument("--root", type=Path)
    parser.add_argument("--file", type=Path)
    parser.add_argument("--metadata", type=Path)
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
    if args.command in {"insurance", "all"}:
        from ebdi.ingestion.insurance import process_insurance

        print(process_insurance(root))
    if args.command in {"analysis", "all"}:
        from ebdi.visualization.reports import analysis

        analysis(root)
    if args.command in {"model", "all"}:
        from ebdi.modeling.severity import train

        train(root)
    if args.command == "explain":
        from ebdi.modeling.explain import explain

        explain(root)
    if args.command in {"history", "all"}:
        from ebdi.ingestion.history import process_history

        print(f"Historical rows: {len(process_history(root))}")
    if args.command in {"exposure", "all"}:
        from ebdi.ingestion.exposure import process_exposure

        print(f"Network rows: {len(process_exposure(root))}")
    if args.command in {"alternative", "all"}:
        from ebdi.metrics.alternatives import alternative_index

        print(f"Alternative index rows: {len(alternative_index(root))}")
    if args.command in {"policy", "all"}:
        from ebdi.modeling.policy import evaluate_policy

        evaluate_policy(root)
    if args.command in {"demographics", "all"}:
        from ebdi.ingestion.demographics import process_demographics

        print(process_demographics(root))
    if args.command in {"material", "all"}:
        from ebdi.ingestion.material import process_material

        print(process_material(root))
    if args.command in {"ncid", "all"}:
        from ebdi.ingestion.ncid import process_ncid

        print(process_ncid(root))
    if args.command in {"extended-analysis", "all"}:
        from ebdi.visualization.extended import extended_analysis

        print(extended_analysis(root))
    if args.command in {"site", "all"}:
        from ebdi.visualization.site import export_site

        print(export_site(root))
    if args.command == "monitor":
        from ebdi.ingestion.monitor import monitor_sources

        report = monitor_sources(root)
        print([(r["id"], r["status"]) for r in report["sources"]])
        if report["attention_required"]:
            raise SystemExit(1)
    if args.command == "claims-import":
        if not args.file or not args.metadata:
            parser.error("claims-import requires --file and --metadata")
        from ebdi.ingestion.claims import import_claims

        print(f"Validated insurer rows: {len(import_claims(root, args.file, args.metadata))}")
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
