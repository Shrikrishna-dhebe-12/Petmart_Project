import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Petmart_Project.settings')  # CORRECT

application = get_wsgi_application()