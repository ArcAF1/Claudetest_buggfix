import sqlite3
import argparse
from .validators import SwedishValidators

BILLING_MAP = {
    'forskott': 'förskott',
    'förskott': 'förskott',
    'prepaid': 'förskott',
    'efterhand': 'efterhand',
    'postpaid': 'efterhand',
    'efterhandsdebitering': 'efterhand',
}

def parse_args():
    p = argparse.ArgumentParser(description="Standardize Phase 1 municipal data")
    p.add_argument('--db', required=True, help='Path to Phase 1 SQLite database')
    return p.parse_args()


def standardize_row(row):
    muni, bill = row
    clean_muni = SwedishValidators.clean_municipality_name(muni)
    bill_clean = bill.lower() if bill else ''
    bill_std = BILLING_MAP.get(bill_clean, bill_clean)
    return clean_muni, bill_std


def run(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT id, municipality, debitering_livsmedel FROM phase1_data')
    rows = cur.fetchall()

    for id_, muni, bill in rows:
        new_muni, new_bill = standardize_row((muni, bill))
        cur.execute(
            'UPDATE phase1_data SET municipality=?, debitering_livsmedel=? WHERE id=?',
            (new_muni, new_bill or None, id_)
        )
    conn.commit()
    conn.close()
    print('Standardization completed')


if __name__ == '__main__':
    args = parse_args()
    run(args.db)
