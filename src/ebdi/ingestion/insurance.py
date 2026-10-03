"""Extract the audited UNESPA 2024 PDF, preserving coverage and selection limits.

The shaded PDF rows do not have complete cell borders. Numeric anchors and
column coordinates retain every row, including wrapped municipality/province
labels; pdfplumber's default extract_tables silently drops alternate rows.
Coordinates are a contract for this hashed release, not arbitrary future PDFs.
"""

import re
from pathlib import Path
from typing import Any

import pandas as pd
import pdfplumber

from ebdi.ingestion.download import raw_path, sha256
from ebdi.utils.io import write_json

SOURCE_URL = "https://www.unespa.es/main-files/uploads/2026/02/NdP-Siniestros-del-seguro-de-auto-2024-FINAL.pdf"
AUDITED_SHA256 = "20211e0e670fc7397e0455320d27166036c357a331b6bc8fddd8fd95d32aa429"


def decimal(value: str) -> float:
    return float(value.replace("%", "").replace(".", "").replace(",", "."))


def municipal_rows(
    page: Any, coverage: str, selection: str, bounds: tuple[float, ...]
) -> list[dict[str, Any]]:
    city_start, province_start, percent_start, end = bounds
    anchors = sorted(
        [
            w
            for w in page.extract_words()
            if percent_start <= w["x0"] < end and re.fullmatch(r"-?\d+,\d+%", w["text"])
        ],
        key=lambda w: w["top"],
    )
    if len(anchors) != 20:
        raise ValueError(f"Expected 20 {coverage}/{selection} rows, got {len(anchors)}")
    centers = [(w["top"] + w["bottom"]) / 2 for w in anchors]
    result = []
    for i, anchor in enumerate(anchors):
        top = (centers[i - 1] + centers[i]) / 2 if i else anchor["top"] - 10
        bottom = (centers[i] + centers[i + 1]) / 2 if i < 19 else anchor["bottom"] + 10

        def cell(left: float, right: float, top: float = top, bottom: float = bottom) -> str:
            return " ".join((page.crop((left, top, right, bottom)).extract_text() or "").split())

        city = cell(city_start, province_start)
        province = cell(province_start, percent_start)
        if not city or not province:
            raise ValueError("Empty municipal label in audited PDF")
        difference = decimal(anchor["text"])
        if difference <= -100 or (difference > 0) != (selection == "higher"):
            raise ValueError("Unexpected municipal relative-difference sign/range")
        result.append(
            {
                "year": 2024,
                "coverage": coverage,
                "municipality": city,
                "province_source": province,
                "selection": selection,
                "source_order": i + 1,
                "relative_difference_pct": difference,
                "source_page": page.page_number,
                "source_table": 8 if selection == "higher" else 9,
            }
        )
    return result


def extract_insurance(
    path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    if sha256(path) != AUDITED_SHA256:
        raise ValueError(
            "UNESPA PDF revision changed; audit layout and definitions before extraction"
        )
    with pdfplumber.open(path) as pdf:
        if len(pdf.pages) != 11:
            raise ValueError("Expected the audited 11-page UNESPA report")
        text = pdf.pages[2].extract_text() or ""
        coverage_rows = []
        for line in text.splitlines():
            match = re.fullmatch(r"(.+?) (\d+,\d+)% (\d+,\d+)% ([\d.]+) €", line)
            if match:
                name, claims, payments, cost = match.groups()
                coverage_rows.append(
                    {
                        "year": 2024,
                        "coverage": name,
                        "claims_share_pct": decimal(claims),
                        "payments_share_pct": decimal(payments),
                        "mean_cost_eur": int(cost.replace(".", "")),
                        "source_page": 3,
                        "source_table": 1,
                    }
                )
        coverage = pd.DataFrame(coverage_rows)
        if len(coverage) != 11 or coverage.coverage.nunique() != 11:
            raise ValueError("Expected all 11 insurance coverages")
        for column in ["claims_share_pct", "payments_share_pct"]:
            if abs(coverage[column].sum() - 100) > 0.05:
                raise ValueError(f"Coverage shares do not reconcile within rounding: {column}")
        total = re.search(r"Total ([\d.]+) ([\d.]+) € ([\d.]+) €", text)
        if not total:
            raise ValueError("Missing national insurance totals")
        national_claims, national_payments, mean_cost = [
            int(v.replace(".", "")) for v in total.groups()
        ]
        province_rows = []
        provincial_texts = [text.split("Tabla/Gráfico 2:", 1)[1], pdf.pages[3].extract_text() or ""]
        for page_number, provincial_text in zip([3, 4], provincial_texts, strict=True):
            for line in provincial_text.splitlines():
                match = re.fullmatch(r"(.+?) (\d[\d.]*) (\d[\d.]*) €", line)
                if match:
                    name, claims, payments = match.groups()
                    province_rows.append(
                        {
                            "year": 2024,
                            "province_source": name,
                            "all_coverage_claims": int(claims.replace(".", "")),
                            "all_coverage_payments_eur": int(payments.replace(".", "")),
                            "source_page": page_number,
                            "source_table": 2,
                        }
                    )
        provinces = pd.DataFrame(province_rows)
        if len(provinces) != 50 or provinces.province_source.nunique() != 50:
            raise ValueError("Expected the 50 published provincial all-coverage rows")
        rows = []
        for page_index, selection, columns in [
            (9, "higher", [(62, 160, 230, 298), (302, 399, 470, 543)]),
            (10, "lower", [(65, 165, 230, 298), (307, 393, 470, 543)]),
        ]:
            page = pdf.pages[page_index]
            if f"Tabla/Gráfico {8 if selection == 'higher' else 9}:" not in (
                page.extract_text() or ""
            ):
                raise ValueError("Municipal table heading changed")
            for code, bounds in zip(["rc_material", "rc_corporal"], columns, strict=True):
                rows.extend(municipal_rows(page, code, selection, tuple(bounds)))
        municipal = pd.DataFrame(rows)
        if municipal.duplicated(["coverage", "municipality"]).any():
            raise ValueError("Duplicate municipal coverage observation")
    quality = {
        "year": 2024,
        "published_date": "2026-02-10",
        "source_url": SOURCE_URL,
        "sha256": sha256(path),
        "national_all_coverage_claims": national_claims,
        "national_all_coverage_payments_eur": national_payments,
        "national_mean_cost_eur": mean_cost,
        "coverage_rows": len(coverage),
        "municipal_rows": len(municipal),
        "material_damage_municipal_rows": int(municipal.coverage.eq("rc_material").sum()),
        "province_rows": len(provinces),
        "provincial_claims_sum": int(provinces.all_coverage_claims.sum()),
        "provincial_claims_difference_from_national": int(provinces.all_coverage_claims.sum())
        - national_claims,
        "provincial_payments_difference_from_national": int(
            provinces.all_coverage_payments_eur.sum()
        )
        - national_payments,
        "municipal_claim_counts_available": False,
        "insured_vehicle_years_available": False,
        "absolute_municipal_probability_available": False,
        "complete_municipal_panel": False,
        "injury_free_event_count_available": False,
        "limitations": [
            "Municipalities above 50,000 inhabitants: only 20 highest and 20 lowest for each coverage, not a full ranking.",
            "Published relative differences, not absolute accident probabilities; labels retained as printed.",
            "Material and bodily claims may overlap for the same accident; no injury-free event total is supplied.",
            "National coverage percentages are rounded; no exact coverage counts are inferred.",
            "Provincial totals cover all insurance categories, including assistance; Ceuta/Melilla are absent from table 2.",
            "Provincial/national reconciliation differences are retained, not redistributed or corrected.",
            "Insurance observations are not merged with DGT counts or the composite index.",
        ],
    }
    return coverage, municipal, provinces, quality


def process_insurance(root: Path) -> dict[str, Any]:
    coverage, municipal, provinces, quality = extract_insurance(raw_path(root, "unespa_motor_2024"))
    output = root / "outputs/tables"
    output.mkdir(parents=True, exist_ok=True)
    for name, frame in [
        ("insurance_coverage", coverage),
        ("insurance_municipal", municipal),
        ("insurance_provinces", provinces),
    ]:
        frame.to_csv(output / f"{name}.csv", index=False)
    write_json(output / "insurance_quality.json", quality)
    return quality
