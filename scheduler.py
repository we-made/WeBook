import subprocess
import time
from datetime import datetime

import schedule

print("== Starting scheduler ==")


def run_pii_sanitization():
    now = datetime.now()
    print(f"[{now}] Sanitizing PII notes")

    process = subprocess.Popen(
        ["python", "manage.py", "sanitize_pii_notes", "30"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = [x.decode("utf-8") for x in process.communicate()]


def hourly_index_update():
    now = datetime.now()
    print(f"[{now}] Updating indexes in Elastic")

    process = subprocess.Popen(
        ["python", "manage.py", "update_index", "--remove", "--age", "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = [x.decode("utf-8") for x in process.communicate()]


def nightly_index_rebuild():
    now = datetime.now()
    print(f"[{now}] Rebuilding indexes in Elastic")

    process = subprocess.Popen(
        ["python", "manage.py", "rebuild_index", "--noinput", "--age=24"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = [x.decode("utf-8") for x in process.communicate()]


def synchronize_all_calendars():
    now = datetime.now()
    print(f"[{now}] Synchronizing all calendars")

    process = subprocess.Popen(
        ["python", "manage.py", "synchronize_all_user_calendars"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = [x.decode("utf-8") for x in process.communicate()]


schedule.every().day.at("01:00").do(synchronize_all_calendars)
schedule.every().day.at("02:00").do(run_pii_sanitization)
schedule.every().hour.do(hourly_index_update)
schedule.every().day.at("03:00").do(nightly_index_rebuild)


while True:
    schedule.run_pending()
    time.sleep(10)
