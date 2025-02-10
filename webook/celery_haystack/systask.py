from webook.systask.tasklib import systask
from .tasks import update_object, remove_object
import subprocess


@systask
def elastic_update_object(id: int, model_name: str) -> bool:
    update_object(id, model_name)


@systask
def elastic_remove_object(id: int, model_name: str) -> bool:
    remove_object(id, model_name)


@systask
def elastic_hourly_index_update() -> bool:
    process = subprocess.Popen(
        ["python", "manage.py", "update_index", "--remove", "--age", "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = [x.decode("utf-8") for x in process.communicate()]

    return True


@systask
def elastic_nightly_reindex() -> bool:
    process = subprocess.Popen(
        ["python", "manage.py", "rebuild_index", "--noinput", "--age=24"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = [x.decode("utf-8") for x in process.communicate()]

    return True
