import os
import subprocess


def run():
    print("== Running pii_sanitize.py ==")
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webook.settings")
    subprocess.run(["python", "manage.py", "sanitize_pii_notes", "30"])
    print("== Done ==")
