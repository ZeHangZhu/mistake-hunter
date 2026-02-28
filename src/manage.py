#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cuotihunter.settings')
    try:
        from django.core.management import execute_from_command_line
        from config import PORT, ALLOW_OTHERS
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Check if we're running the runserver command
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        # Modify arguments to use our config settings
        host = '0.0.0.0' if ALLOW_OTHERS else '127.0.0.1'
        sys.argv = [sys.argv[0], 'runserver', f'{host}:{PORT}']
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
