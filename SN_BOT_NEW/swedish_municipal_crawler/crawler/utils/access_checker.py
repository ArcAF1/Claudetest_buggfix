import argparse
import sqlite3
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import requests
from bs4 import BeautifulSoup


def parse_args():
    p = argparse.ArgumentParser(description='Check robots.txt and login requirements')
    p.add_argument('--db', required=True, help='Path to Phase 1 SQLite database')
    p.add_argument('--limit', type=int, default=None, help='Limit number of sites to check')
    return p.parse_args()


def load_sites(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT source_url FROM phase1_data WHERE source_url IS NOT NULL')
    urls = [row[0] for row in cur.fetchall()]
    conn.close()
    domains = sorted({urlparse(u).netloc for u in urls if u})
    return domains


def check_robot(domain):
    rp = RobotFileParser()
    rp.set_url(f'https://{domain}/robots.txt')
    try:
        rp.read()
        return rp.can_fetch('*', '/')
    except Exception:
        return True


def check_login(url):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        if soup.find('input', {'type': 'password'}) or 'login' in url.lower():
            return True
    except Exception:
        pass
    return False


def run(db_path, limit):
    domains = load_sites(db_path)
    if limit:
        domains = domains[:limit]
    for dom in domains:
        allowed = check_robot(dom)
        login_required = check_login(f'https://{dom}')
        status = []
        if not allowed:
            status.append('disallowed by robots.txt')
        if login_required:
            status.append('login required')
        if status:
            print(f'{dom}: {", ".join(status)}')


if __name__ == '__main__':
    args = parse_args()
    run(args.db, args.limit)
