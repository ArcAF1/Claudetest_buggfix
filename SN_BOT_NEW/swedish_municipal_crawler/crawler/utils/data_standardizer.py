import argparse
import sqlite3
from pathlib import Path

from .validators import SwedishValidators


DEBITERING_SYNONYMS = {
    'f\u00f6rskott': 'f\u00f6rskott',
    'i f\u00f6rskott': 'f\u00f6rskott',
    'forhandsdebitering': 'f\u00f6rskott',
    'efterhand': 'efterhand',
    'i efterskott': 'efterhand',
    'efterskott': 'efterhand',
}


def normalize_debitering(value: str) -> str:
    if not value:
        return value
    cleaned = value.strip().lower().replace('-', ' ')
    for synonym, canonical in DEBITERING_SYNONYMS.items():
        if synonym in cleaned:
            return canonical
    return cleaned


def standardize_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, municipality, debitering_livsmedel FROM phase1_data"
    )
    rows = cursor.fetchall()
    for row_id, municipality, debitering in rows:
        clean_name = SwedishValidators.clean_municipality_name(municipality)
        normalized_deb = normalize_debitering(debitering)
        if clean_name != municipality or normalized_deb != debitering:
            cursor.execute(
                "UPDATE phase1_data SET municipality=?, debitering_livsmedel=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (clean_name, normalized_deb, row_id),
            )

    conn.commit()
    conn.close()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Standardize municipality names and billing models in the Phase 1 database"
    )
    parser.add_argument("--db", required=True, help="Path to Phase 1 SQLite database")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")
    standardize_db(db_path)
    print("Standardization completed")


if __name__ == "__main__":
    main()
