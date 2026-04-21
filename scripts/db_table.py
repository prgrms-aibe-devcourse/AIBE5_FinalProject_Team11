#!/usr/bin/env python3
"""
db_table.py — Pretty-print yogadb contents from the running Postgres container.

Usage:
    python scripts/db_table.py                     # list all poses (default)
    python scripts/db_table.py poses               # same
    python scripts/db_table.py poses --limit 20
    python scripts/db_table.py benefits --pose warrior_i
    python scripts/db_table.py contraindications --kill-switch
    python scripts/db_table.py keywords --pose warrior_i
    python scripts/db_table.py summary             # row counts per table
    python scripts/db_table.py poses --search "chair"
    python scripts/db_table.py qa                  # all Q&A pairs
    python scripts/db_table.py qa --pose mountain_pose
    python scripts/db_table.py qa --type benefits
    python scripts/db_table.py qa --type what_is --limit 10
"""

import argparse
import os
import sys

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    sys.exit(
        "psycopg2 not found. Install it:\n"
        "  pip install psycopg2-binary\n"
        "Or run via Docker:\n"
        "  docker exec -it yoga-api-postgres-1 psql -U postgres -d yogadb"
    )

# ── connection ──────────────────────────────────────────────────────────────

DEFAULT_DSN = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "8879")),
    "dbname": os.getenv("DB_NAME", "yogadb"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "postgres"),
}


def connect():
    try:
        return psycopg2.connect(**DEFAULT_DSN)
    except psycopg2.OperationalError as e:
        sys.exit(f"Cannot connect to Postgres: {e}\nIs the Docker stack running?")


# ── formatting ───────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
GREEN  = "\033[32m"
RED    = "\033[31m"
DIM    = "\033[2m"

def _trunc(val, width):
    s = str(val) if val is not None else ""
    return s[:width - 1] + "…" if len(s) > width else s

def print_table(rows, headers, widths, colour_col=None, colour_fn=None):
    sep = "┼".join("─" * (w + 2) for w in widths)
    top = "┬".join("─" * (w + 2) for w in widths)
    bot = "┴".join("─" * (w + 2) for w in widths)

    print(f"┌{top}┐")
    header_cells = " │ ".join(
        f"{BOLD}{CYAN}{h:<{widths[i]}}{RESET}" for i, h in enumerate(headers)
    )
    print(f"│ {header_cells} │")
    print(f"├{sep}┤")

    for row in rows:
        cells = []
        for i, val in enumerate(row):
            cell = _trunc(val, widths[i])
            if colour_col is not None and i == colour_col and colour_fn:
                cell = colour_fn(val) + f"{cell:<{widths[i]}}" + RESET
            else:
                cell = f"{cell:<{widths[i]}}"
            cells.append(cell)
        print(f"│ {' │ '.join(cells)} │")

    print(f"└{bot}┘")
    print(f"{DIM}  {len(rows)} row(s){RESET}")


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_poses(cur, args):
    sql = """
        SELECT p.pose_id,
               p.canonical_name,
               p.difficulty_rank,
               p.aeo_summary,
               COUNT(DISTINCT b.id)  AS benefits,
               COUNT(DISTINCT c.id)  AS contraindications
        FROM   poses p
        LEFT JOIN pose_benefits b ON b.pose_id = p.pose_id
        LEFT JOIN pose_contraindications c ON c.pose_id = p.pose_id
    """
    params = []
    if args.search:
        sql += " WHERE LOWER(p.canonical_name) LIKE %s OR LOWER(p.aeo_summary) LIKE %s"
        term = f"%{args.search.lower()}%"
        params += [term, term]
    sql += " GROUP BY p.pose_id ORDER BY p.canonical_name"
    if args.limit:
        sql += " LIMIT %s"
        params.append(args.limit)

    cur.execute(sql, params)
    rows = cur.fetchall()

    headers = ["pose_id", "canonical_name", "diff", "aeo_summary", "ben", "ctr"]
    widths  = [30, 32, 4, 55, 3, 3]
    print_table(rows, headers, widths)


def cmd_benefits(cur, args):
    sql = "SELECT b.pose_id, b.tag, b.weight FROM pose_benefits b"
    params = []
    if args.pose:
        sql += " WHERE b.pose_id LIKE %s"
        params.append(f"%{args.pose}%")
    sql += " ORDER BY b.pose_id, b.weight DESC"
    if args.limit:
        sql += " LIMIT %s"
        params.append(args.limit)

    cur.execute(sql, params)
    rows = cur.fetchall()

    def weight_colour(val):
        try:
            w = float(val)
            return GREEN if w >= 0.8 else (YELLOW if w >= 0.5 else DIM)
        except (TypeError, ValueError):
            return RESET

    headers = ["pose_id", "tag", "weight"]
    widths  = [40, 28, 6]
    print_table(rows, headers, widths, colour_col=2, colour_fn=weight_colour)


def cmd_contraindications(cur, args):
    sql = """
        SELECT c.pose_id, c.condition, c.severity, c.kill_switch, c.instruction
        FROM   pose_contraindications c
    """
    clauses, params = [], []
    if args.pose:
        clauses.append("c.pose_id LIKE %s")
        params.append(f"%{args.pose}%")
    if args.kill_switch:
        clauses.append("c.kill_switch = TRUE")
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY c.kill_switch DESC, c.severity, c.pose_id"
    if args.limit:
        sql += " LIMIT %s"
        params.append(args.limit)

    cur.execute(sql, params)
    rows = cur.fetchall()

    def ks_colour(val):
        return RED if val else DIM

    headers = ["pose_id", "condition", "severity", "kill", "instruction"]
    widths  = [32, 30, 18, 4, 40]
    print_table(rows, headers, widths, colour_col=3, colour_fn=ks_colour)


def cmd_keywords(cur, args):
    sql = "SELECT k.pose_id, k.keyword FROM pose_keywords k"
    params = []
    if args.pose:
        sql += " WHERE k.pose_id LIKE %s"
        params.append(f"%{args.pose}%")
    sql += " ORDER BY k.pose_id"
    if args.limit:
        sql += " LIMIT %s"
        params.append(args.limit)

    cur.execute(sql, params)
    rows = cur.fetchall()

    headers = ["pose_id", "keyword"]
    widths  = [40, 60]
    print_table(rows, headers, widths)


def cmd_qa(cur, args):
    sql = """
        SELECT q.pose_id, q.question_type, q.language,
               q.question, q.answer
        FROM   pose_qa q
    """
    clauses, params = [], []
    if args.pose:
        clauses.append("q.pose_id LIKE %s")
        params.append(f"%{args.pose}%")
    if args.type:
        clauses.append("q.question_type = %s")
        params.append(args.type)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY q.pose_id, q.question_type"
    if args.limit:
        sql += " LIMIT %s"
        params.append(args.limit)

    cur.execute(sql, params)
    rows = cur.fetchall()

    headers = ["pose_id", "type", "lang", "question", "answer"]
    widths  = [30, 18, 4, 42, 52]
    print_table(rows, headers, widths)


def cmd_summary(cur, _args):
    tables = [
        "poses", "pose_benefits", "pose_contraindications",
        "pose_focus", "pose_keywords", "pose_qa",
    ]
    rows = []
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        rows.append((t, count))

    headers = ["table", "rows"]
    widths  = [28, 8]
    print_table(rows, headers, widths)


# ── main ──────────────────────────────────────────────────────────────────────

COMMANDS = {
    "poses":            cmd_poses,
    "benefits":         cmd_benefits,
    "contraindications":cmd_contraindications,
    "keywords":         cmd_keywords,
    "qa":               cmd_qa,
    "summary":          cmd_summary,
}

def main():
    parser = argparse.ArgumentParser(
        description="Print yogadb contents as formatted tables.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("table", nargs="?", default="poses",
                        choices=list(COMMANDS),
                        help="Which view to display (default: poses)")
    parser.add_argument("--limit", "-n", type=int, default=None,
                        help="Max rows to return")
    parser.add_argument("--pose", "-p", type=str, default=None,
                        help="Filter by pose_id substring")
    parser.add_argument("--search", "-s", type=str, default=None,
                        help="Search canonical_name / aeo_summary (poses only)")
    parser.add_argument("--kill-switch", "-k", action="store_true",
                        help="Show only kill-switch contraindications")
    parser.add_argument("--type", "-t", type=str, default=None,
                        metavar="QTYPE",
                        help="Filter qa by question_type "
                             "(what_is|benefits|contraindications|body_parts|how_to)")

    args = parser.parse_args()

    conn = connect()
    try:
        with conn.cursor() as cur:
            COMMANDS[args.table](cur, args)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
