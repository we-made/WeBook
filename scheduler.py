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


schedule.every().day.at("02:00").do(run_pii_sanitization)


while True:
    schedule.run_pending()
    time.sleep(10)
