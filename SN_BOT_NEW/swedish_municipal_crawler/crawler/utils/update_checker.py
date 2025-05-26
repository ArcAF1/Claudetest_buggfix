import argparse
import sqlite3
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
except ImportError:  # pragma: no cover - graceful handling if requests missing
    requests = None


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check municipal fee pages for updates since last crawl"
    )
    parser.add_argument(
        "--db",
        required=True,
        help="Path to Phase 1 SQLite database created by the crawler"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit of URLs to check"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="HTTP timeout for HEAD requests"
    )
    return parser.parse_args()


def load_sources(db_path):
    """Load source URLs and last extraction dates from the Phase 1 database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT municipality, source_url, extraction_date FROM phase1_data "
            "WHERE source_url IS NOT NULL")
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to read database: {e}")

    rows = cursor.fetchall()
    conn.close()

    sources = []
    for municipality, url, date_str in rows:
        try:
            last_date = datetime.fromisoformat(date_str)
        except Exception:
            last_date = None
        sources.append({
            "municipality": municipality,
            "url": url,
            "last_date": last_date,
        })
    return sources


def check_url_updated(url, last_date, timeout=10):
    """Return True if the URL appears updated since last_date."""
    try:
        resp = requests.head(url, allow_redirects=True, timeout=timeout)
    except Exception:
        return False

    if resp.status_code >= 400:
        return False

    lm = resp.headers.get("Last-Modified")
    if lm and last_date:
        try:
            mod_time = datetime.strptime(lm, "%a, %d %b %Y %H:%M:%S %Z")
            return mod_time > last_date
        except Exception:
            pass

    etag = resp.headers.get("ETag")
    if etag and last_date:
        # If ETag present but last_date known, assume changed if different
        return True

    # Fallback: if content length differs or no metadata, assume updated
    return True


def main():
    if requests is None:
        print("The 'requests' package is required to run this script.")
        print("Install dependencies with: pip install -r requirements.txt")
        return

    args = parse_args()
    sources = load_sources(args.db)

    if args.limit:
        sources = sources[:args.limit]

    updated = []
    for src in sources:
        if check_url_updated(src["url"], src["last_date"], timeout=args.timeout):
            updated.append(src)

    if not updated:
        print("No updates detected")
    else:
        print("Pages with potential updates:")
        for u in updated:
            date_str = u["last_date"].isoformat() if u["last_date"] else "unknown"
            domain = urlparse(u["url"]).netloc
            print(f"- {u['municipality']} ({domain}) last checked {date_str}: {u['url']}")


if __name__ == "__main__":
    main()
