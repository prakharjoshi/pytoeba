import os
import sys

def pytest_configure():
    # change this to run the tests on your machine
    # hardcoded for now, checking whether env vars
    # are set or not is pita
    os.environ['DJANGO_SETTINGS_MODULE'] = 'pytoeba_dev.settings'
    settings_path = '/home/lool0/dabblings/pytoeba_dev/'
    sys.path.append(settings_path)
