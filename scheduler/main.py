import time

import schedule
from jobs.pii_sanitize import run as pii_sanitize_run

print("== Starting scheduler ==")

pii_sanitize_run()

schedule.every(1).minutes.do(pii_sanitize_run)

while True:
    schedule.run_pending()
    time.sleep(1)
