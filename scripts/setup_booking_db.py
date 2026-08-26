import subprocess, secrets

pw = secrets.token_urlsafe(20)

sql = f"""
CREATE USER IF NOT EXISTS 'booking_user'@'localhost' IDENTIFIED BY '{pw}';
GRANT ALL PRIVILEGES ON booking_system.* TO 'booking_user'@'localhost';
FLUSH PRIVILEGES;
SELECT User, Host FROM mysql.user WHERE User='booking_user';
"""

result = subprocess.run(
    ["sudo", "mysql"],
    input=sql, text=True, capture_output=True
)
print(result.stdout)
print(result.stderr)
print(f"DB_USER=booking_user")
print(f"DB_PASSWORD={pw}")
