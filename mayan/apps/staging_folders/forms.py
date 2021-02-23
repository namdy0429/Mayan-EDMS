import json
import logging

from django import forms
from django.db.models import Model
from django.db.models.query import QuerySet
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.sources.classes import SourceBackend
from mayan.apps.sources.forms import UploadBaseForm

logger = logging.getLogger(name=__name__)


class StagingUploadForm(UploadBaseForm):
    """
    Form that show all the files in the staging folder specified by the
    StagingFile class passed as 'cls' argument
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.fields['staging_file_id'].choices = [
                (
                    staging_file.encoded_filename, force_text(s=staging_file)
                ) for staging_file in self.source.get_backend_instance().get_files()
            ]
        except Exception as exception:
            logger.error('exception: %s', exception)

    staging_file_id = forms.ChoiceField(label=_('Staging file'))
