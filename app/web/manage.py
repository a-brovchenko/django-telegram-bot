import os
import sys


def main():
    
    if 'runserver' in sys.argv:
            if os.environ.get('RUN_MAIN', None) != 'true':
                from tg_bot.bot import run_bot
                # from multiprocessing import Process
                # p = Process(target=run_bot).start()
                import threading
                thr = threading.Thread(target=run_bot, name='Daemon', daemon=True).start()
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
    print('start django')
    main()
