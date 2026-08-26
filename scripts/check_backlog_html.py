import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'AI_automate.settings'
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from dashboard import views

User = get_user_model()
user = User.objects.filter(is_staff=True).first()
factory = RequestFactory()
req = factory.get('/owner/backlog/')
req.user = user

from django.test.utils import setup_test_environment
setup_test_environment()

resp = views.backlog_view(req)
html = resp.content.decode('utf-8')

checks = ['backlogDetailModal', 'openBacklogModal', 'btnApproveBacklog', 'btnSaveBacklog', 'blog_categories']
for c in checks:
    found = c in html
    print(f"  {c}: {'OK' if found else 'MISSING'}")
