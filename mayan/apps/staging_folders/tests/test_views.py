from mayan.apps.testing.tests.base import GenericViewTestCase

from ..permissions import permission_sources_view
from ..source_backends.literals import SOURCE_UNCOMPRESS_CHOICE_ALWAYS

from .mixins import (
    StagingFolderTestMixin, StagingFolderViewTestMixin,
)


class StagingFolderViewTestCase(
    StagingFolderTestMixin, StagingFolderViewTestMixin, GenericViewTestCase
):
    def setUp(self):
        super().setUp()
        self._create_test_staging_folder()
        self._copy_test_document()

    def test_staging_file_delete_no_permission(self):
        staging_file_count = len(list(self.test_staging_folder.get_files()))
        staging_file = list(self.test_staging_folder.get_files())[0]

        response = self._request_test_staging_file_delete_view(
            staging_folder=self.test_staging_folder, staging_file=staging_file
        )
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            staging_file_count,
            len(list(self.test_staging_folder.get_files()))
        )

    def test_staging_file_delete_with_permission(self):
        self.grant_permission(permission=permission_sources_view)

        staging_file_count = len(list(self.test_staging_folder.get_files()))
        staging_file = list(self.test_staging_folder.get_files())[0]

        response = self._request_test_staging_file_delete_view(
            staging_folder=self.test_staging_folder, staging_file=staging_file
        )
        self.assertEqual(response.status_code, 302)

        self.assertNotEqual(
            staging_file_count,
            len(list(self.test_staging_folder.get_files()))
        )
