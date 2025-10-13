import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.telegrom.bot import main

if __name__ == "__main__":
    main()
