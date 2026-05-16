import sqlite3
from datetime import date, datetime, timezone, timedelta

DB = "db.sqlite3"
BKK = timezone(timedelta(hours=7))

target = date(2026, 5, 16)

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

cur.execute("""
    SELECT id, title, start_datetime, category, is_completed, assigned_to
    FROM dashboard_calendarevent
    WHERE date(start_datetime) <= ? AND (end_datetime IS NULL OR date(end_datetime) >= ?)
    ORDER BY start_datetime
""", (str(target), str(target)))

rows = cur.fetchall()
pending = [r for r in rows if not r['is_completed']]
done    = [r for r in rows if r['is_completed']]

print(f"=== Calendar: {target} ===")
print(f"Total: {len(rows)} | Done: {len(done)} | Pending: {len(pending)}")
print()
print(f"--- Pending ({len(pending)}) ---")
for r in pending:
    print(f"  [ ] [{r['id']}] {r['title']} ({r['category']})")
print()
print(f"--- Done ({len(done)}) ---")
for r in done:
    print(f"  [x] [{r['id']}] {r['title']} ({r['category']})")

con.close()
