import sys
import os
import signal
import django
import pymysql
import psutil
from mappingsite.views import scrprocess

pymysql.version_info = (1, 3, 13, "final", 0)
pymysql.install_as_MySQLdb()

my_django_shutdown_signal = django.dispatch.Signal()

def _forward_to_django_shutdown_signal(signal_int, frame):
    for proc in psutil.process_iter(attrs=["pid"]):
        if proc.info["pid"] == scrprocess.pid:
                os.killpg(os.getpgid(proc.info["pid"]), signal.SIGTERM)
    sys.exit(0);

signal.signal(signal.SIGINT, _forward_to_django_shutdown_signal)