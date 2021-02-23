from django.utils.translation import ugettext_lazy as _

from mayan.apps.sources.queues import queue_sources_fast

queue_sources_fast.add_task_type(
    label=_('Generate staging file image'),
    dotted_path='mayan.apps.staging_folders.tasks.task_generate_staging_file_image'
)
