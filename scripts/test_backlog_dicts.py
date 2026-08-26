import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from dashboard.views import _backlog_qs_to_dicts
from marketing.models import ContentBacklog

qs = ContentBacklog.objects.all().order_by("num")[:8]
items = _backlog_qs_to_dicts(qs)
for i in items:
    art_status = i["article_status"] or "-"
    art_url = i["article_edit_url"] or "-"
    print(f'#{i["id"]} [{i["status"]}] art={art_status} | {i["topic"][:45]}')
    if art_url != "-":
        print(f'   url={art_url}')
print("OK")
