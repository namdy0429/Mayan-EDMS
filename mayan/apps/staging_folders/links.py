from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link
from mayan.apps.sources.permissions import permission_sources_view

from .icons import icon_staging_file_delete

link_staging_file_delete = Link(
    args=('source.pk', 'object.encoded_filename',), keep_query=True,
    icon=icon_staging_file_delete,
    permissions=(permission_sources_view,),
    tags='dangerous', text=_('Delete'),
    view='staging_folders:staging_file_delete',
)
