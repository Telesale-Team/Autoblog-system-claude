import pymysql
from datetime import date, datetime, timezone, timedelta

# DB config (จาก .env)
DB_CONFIG = {
    "host": "192.168.1.203",
    "port": 3306,
    "db": "peyo_agent",
    "user": "peyo",
    "password": "peyo2026!",
    "charset": "utf8mb4",
}

BKK = timezone(timedelta(hours=7))
target = date.today()

con = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
cur = con.cursor()

# ── วันนี้: เริ่มวันนี้เท่านั้น (ตรงกับที่เห็นในปฏิทิน)
cur.execute("""
    SELECT id, title, start_datetime, category, is_completed, assigned_to
    FROM dashboard_calendarevent
    WHERE DATE(start_datetime) = %s
    ORDER BY start_datetime
""", (str(target),))

rows    = cur.fetchall()
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

# ── งานค้างจากก่อน (เริ่มก่อนวันนี้ ยังไม่เสร็จ)
cur.execute("""
    SELECT id, title, DATE(start_datetime) as start_date, category
    FROM dashboard_calendarevent
    WHERE DATE(start_datetime) < %s AND is_completed = 0
    ORDER BY start_datetime
""", (str(target),))

overdue = cur.fetchall()
if overdue:
    print(f"\n--- งานค้างจากก่อน ({len(overdue)}) ---")
    for r in overdue:
        print(f"  [!] [{r['id']}] {r['title']} (เริ่ม {r['start_date']})")

con.close()
