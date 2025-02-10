from datetime import datetime
from webook.systask.tasklib import systask
import subprocess


@systask
def sanitize_pii_notes():
    now = datetime.now()
    print(f"[{now}] Sanitizing PII notes")

    process = subprocess.Popen(
        ["python", "manage.py", "sanitize_pii_notes", "30"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = [x.decode("utf-8") for x in process.communicate()]
