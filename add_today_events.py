import sqlite3

DB = "db.sqlite3"
today = "2026-05-16"

events = [
    ("Fix: Sidebar — แก้ route Portfolio (dashboard:projects)", f"{today} 09:00:00", "action", 1, "Claude Code"),
    ("Fix: Sidebar — pin System section to bottom", f"{today} 09:30:00", "action", 1, "Claude Code"),
    ("Fix: Sidebar — padding-bottom scroll clearance", f"{today} 09:45:00", "action", 1, "Claude Code"),
    ("Fix: docs_index.html — rewrite to base.html design system", f"{today} 10:00:00", "action", 1, "Claude Code"),
    ("Feature: Docs Viewer — split-pane AJAX ไม่เปลี่ยน URL", f"{today} 10:30:00", "delivery", 1, "Claude Code"),
    ("UI: Docs left panel — VS Code flat list style", f"{today} 11:00:00", "action", 1, "Claude Code"),
    ("Feature: Docs Viewer — AdminLTE sidebar + 29-menu agent roadmap", f"{today} 11:30:00", "delivery", 1, "Claude Code"),
]

con = sqlite3.connect(DB)
cur = con.cursor()

for title, start, cat, done, assigned in events:
    cur.execute(
        "INSERT INTO dashboard_calendarevent "
        "(title, start_datetime, category, is_completed, assigned_to, color, all_day, is_system, description, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, '#28a745', 0, 0, '', datetime('now'), datetime('now'))",
        (title, start, cat, done, assigned),
    )
    print(f"Added: {title}")

con.commit()
con.close()
print("Done — 7 events added")
