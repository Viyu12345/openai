import os
import django
from django.core.management import call_command

# Create the project
call_command('startapp', 'ai', '.')

# Set the environment variable for Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Farmer.settings')

# Initialize Django
django.setup()
