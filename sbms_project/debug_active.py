import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sbms_project.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.create_user(username='debugactive', password='secret123')
client = Client()
client.force_login(user)
resp = client.get('/?business_type=hotel')
html = resp.content.decode('utf-8')
needle = 'sidebar-btn'
idx = html.find(needle)
print(resp.status_code)
print('HAS1', 'value="hotel" class="sidebar-btn active"' in html)
print('HAS2', 'aria-current="page"' in html)
print(html[idx-30:idx+120])
print('Context business_type:', resp.context['business_type'])
