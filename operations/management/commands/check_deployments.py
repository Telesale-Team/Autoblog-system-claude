"""ตรวจสุขภาพทุก Deployment ที่เปิดการเฝ้าดูไว้

รันมือ:
    python manage.py check_deployments
รันตัวเดียว:
    python manage.py check_deployments --id 3
ตั้งเวลา (บน server ใส่ใน cron หรือ systemd timer ทุก 5 นาที):
    */5 * * * * cd /home/dphoompat/peyo-agent && venv/bin/python manage.py check_deployments

ทำงานแบบ pull — ยิง HTTP ออกไปหาแต่ละระบบ ไม่ต้องแก้โค้ดฝั่งลูกค้า
ถ้า deployment ตั้ง monitor_path ไว้ จะยิงซ้ำอีกครั้งเพื่อดึงตัวเลขธุรกิจ
"""
import time

import requests
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from operations.models import Deployment, HealthCheck

TIMEOUT = 12
UA = "NoodeeMonitor/1.0 (+https://noodee-bootbiz.com)"


class Command(BaseCommand):
    help = "ยิงเช็คสถานะทุก Deployment แล้วบันทึกผลลง HealthCheck"

    def add_arguments(self, parser):
        parser.add_argument("--id", type=int, default=None,
                            help="เช็คเฉพาะ deployment id นี้")
        parser.add_argument("--dry-run", action="store_true",
                            help="แสดงผลอย่างเดียว ไม่บันทึกลง DB")

    def handle(self, *args, **opts):
        qs = Deployment.objects.filter(is_monitored=True).exclude(base_url="")
        if opts["id"]:
            qs = Deployment.objects.filter(pk=opts["id"])

        if not qs.exists():
            self.stdout.write(self.style.WARNING(
                "ไม่มี deployment ที่เช็คได้ — ต้องเปิด is_monitored และใส่ base_url ก่อน"))
            return

        for dep in qs:
            result = self._check(dep)

            if opts["dry_run"]:
                self.stdout.write(f"[dry-run] {dep.name}: {result}")
                continue

            HealthCheck.objects.create(deployment=dep, **result)

            if result["is_up"]:
                self.stdout.write(self.style.SUCCESS(
                    f"  UP    {dep.name:28s} {result['status_code']} {result['response_ms']} ms"
                    + (f" v{result['version']}" if result["version"] else "")))
            else:
                self.stdout.write(self.style.ERROR(
                    f"  DOWN  {dep.name:28s} {result['error'][:70]}"))

    # ── ยิงเช็ค 1 ตัว ──
    def _check(self, dep):
        out = dict(is_up=False, status_code=None, response_ms=None,
                   error="", version="", deployed_at=None, metrics=[])

        url = dep.check_url
        start = time.monotonic()
        try:
            r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": UA},
                             allow_redirects=True)
            out["response_ms"] = int((time.monotonic() - start) * 1000)
            out["status_code"] = r.status_code
            out["is_up"] = r.status_code < 400
            if not out["is_up"]:
                out["error"] = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            out["response_ms"] = int((time.monotonic() - start) * 1000)
            out["error"] = f"{type(e).__name__}: {e}"[:500]
            return out

        # ── ดึงตัวเลขธุรกิจ ถ้าระบบปลายทางรองรับ ──
        if out["is_up"] and dep.monitor_path:
            self._fetch_metrics(dep, out)

        return out

    def _fetch_metrics(self, dep, out):
        headers = {"User-Agent": UA}
        if dep.monitor_token:
            headers["Authorization"] = f"Bearer {dep.monitor_token}"
        try:
            r = requests.get(dep.monitor_url, timeout=TIMEOUT, headers=headers)
            if r.status_code >= 400:
                return
            data = r.json()
        except (requests.RequestException, ValueError):
            return

        out["version"] = str(data.get("version", ""))[:80]
        raw_dt = data.get("deployed_at")
        if raw_dt:
            out["deployed_at"] = parse_datetime(str(raw_dt))
        metrics = data.get("metrics")
        if isinstance(metrics, list):
            out["metrics"] = metrics[:6]
