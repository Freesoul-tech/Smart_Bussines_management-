import os
import sys
import pathlib
# Ensure project root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sbms_project.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
settings.ALLOWED_HOSTS = ['testserver', 'localhost']

user = get_user_model().objects.create_user(username='inspect_user2', password='secret123')
client = Client()
client.force_login(user)
response = client.get(reverse('dashboard:index'), {'business_type': 'hotel'})
html = response.content.decode('utf-8')
print('status=', response.status_code)
idx = html.find('sidebar-btn')
print('sidebar-btn index', idx)
if idx != -1:
    start = max(0, idx-120)
    end = min(len(html), idx+200)
    print(html[start:end])
else:
    print('sidebar-btn not found')

print('\nExact substring present:', 'value="hotel" class="sidebar-btn active"' in html)
