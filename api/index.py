import os
from django.core.wsgi import get_wsgi_application
from vercel_wsgi import handle

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studbud.settings")

app = get_wsgi_application()
handler = handle(app)
