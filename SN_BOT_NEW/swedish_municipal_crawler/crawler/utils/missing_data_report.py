import sqlite3
import argparse
import json

FIELDS = ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']


def parse_args():
    p = argparse.ArgumentParser(description='Report municipalities with missing Phase 1 fields')
    p.add_argument('--db', required=True, help='Path to Phase 1 SQLite database')
    p.add_argument('--out', default='missing_data.json', help='Output JSON file')
    return p.parse_args()


def run(db_path, out_file):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    placeholders = ' OR '.join(f"{f} IS NULL" for f in FIELDS)
    query = f"SELECT municipality, {', '.join(FIELDS)} FROM phase1_data WHERE {placeholders}"
    rows = cur.execute(query).fetchall()
    conn.close()
    result = []
    for row in rows:
        muni = row[0]
        data = dict(zip(FIELDS, row[1:]))
        result.append({'municipality': muni, 'missing_fields': [k for k, v in data.items() if v is None]})
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f'Report written to {out_file}')


if __name__ == '__main__':
    args = parse_args()
    run(args.db, args.out)
