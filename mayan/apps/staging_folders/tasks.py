import logging

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import OperationalError

from mayan.celery import app

from mayan.apps.lock_manager.backends.base import LockingBackend
from mayan.apps.lock_manager.exceptions import LockError

logger = logging.getLogger(name=__name__)


@app.task()
def task_generate_staging_file_image(
    staging_folder_pk, encoded_filename, *args, **kwargs
):
    Source = apps.get_model(
        app_label='sources', model_name='Source'
    )
    staging_folder = Source.objects.get(pk=staging_folder_pk)
    staging_file = staging_folder.get_backend_instance().get_file(
        encoded_filename=encoded_filename
    )

    return staging_file.generate_image(*args, **kwargs)
