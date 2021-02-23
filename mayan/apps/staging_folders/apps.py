from django.apps import apps
from django.db.models.signals import pre_delete
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.acls.links import link_acl_list
from mayan.apps.acls.permissions import (
    permission_acl_edit, permission_acl_view
)
from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.classes import MissingItem
from mayan.apps.common.signals import (
    signal_post_initial_setup, signal_post_upgrade
)
from mayan.apps.converter.links import link_transformation_list
from mayan.apps.documents.menus import menu_documents
from mayan.apps.logging.classes import ErrorLog
from mayan.apps.navigation.classes import SourceColumn
from mayan.apps.views.html_widgets import TwoStateWidget
from mayan.apps.common.menus import (
    menu_list_facet, menu_object, menu_related, menu_secondary, menu_setup
)

from .html_widgets import StagingFileThumbnailWidget
from .links import link_staging_file_delete


class StagingFoldersApp(MayanAppConfig):
    app_namespace = 'staging_folders'
    app_url = 'staging_folders'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.staging_folders'
    verbose_name = _('Staging folders')

    def ready(self):
        super().ready()
        #Source = self.get_model(model_name='Source')

        #FIXME
        from .source_backends import StagingFile

        # ~ SourceColumn(
            # ~ attribute='label', is_identifier=True, is_sortable=True,
            # ~ source=Source
        # ~ )
        # ~ SourceColumn(
            # ~ attribute='get_backend_label', include_label=True,
            # ~ label=_('Type'), source=Source
        # ~ )
        # ~ SourceColumn(
            # ~ attribute='enabled', include_label=True, is_sortable=True,
            # ~ source=Source,
            # ~ widget=TwoStateWidget
        # ~ )

        SourceColumn(
            func=lambda context: context['object'].get_date_time_created(),
            label=_('Created'), source=StagingFile,
        )

        SourceColumn(
            source=StagingFile,
            label=_('Thumbnail'),
            #func=lambda context: html_widget.render(
            #    instance=context['object'],
            #)
            widget=StagingFileThumbnailWidget
        )

        menu_object.bind_links(
            links=(link_staging_file_delete,), sources=(StagingFile,)
        )
