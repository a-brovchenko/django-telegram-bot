import os
import sys
import threading
from tg_bot.bot import run_bot
from multiprocessing import Process

def main():

    if 'runserver' in sys.argv:
            if os.environ.get('RUN_MAIN', None) != 'true':
                p = Process(target=run_bot).start()

    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
