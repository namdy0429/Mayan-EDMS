import shutil

from django.db.models import Q

from mayan.apps.documents.tests.literals import TEST_SMALL_DOCUMENT_PATH
from mayan.apps.storage.utils import fs_cleanup, mkdtemp

from ..models import Source
from ..staging_folder_backends import SourceBackendStagingFolder

from .literals import TEST_STAGING_PREVIEW_WIDTH


class StagingFolderAPIViewTestMixin:
    def setUp(self):
        super().setUp()
        self.test_staging_folders = []

    def tearDown(self):
        for test_staging_folder in self.test_staging_folders:
            fs_cleanup(filename=test_staging_folder.folder_path)
            self.test_staging_folders.remove(test_staging_folder)

        super().tearDown()

    def _request_test_staging_folder_create_api_view(self):
        return self.post(
            viewname='rest_api:stagingfolder-list', data={
                'label': TEST_SOURCE_LABEL,
                'folder_path': mkdtemp(),
                'preview_width': TEST_STAGING_PREVIEW_WIDTH,
                'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER,
            }
        )

        self.test_staging_folder = StagingFolderSource.objects.first()
        self.test_staging_folders.append(self.test_staging_folder)

    def _request_test_staging_folder_delete_api_view(self):
        return self.delete(
            viewname='rest_api:stagingfolder-detail', kwargs={
                'pk': self.test_staging_folder.pk
            }
        )

    def _request_test_staging_folder_edit_api_view(self, extra_data=None, verb='patch'):
        data = {
            'label': TEST_SOURCE_LABEL_EDITED,
        }

        if extra_data:
            data.update(extra_data)

        return getattr(self, verb)(
            viewname='rest_api:stagingfolder-detail', kwargs={
                'pk': self.test_staging_folder.pk
            }, data=data
        )

    def _request_test_staging_folder_list_api_view(self):
        return self.get(viewname='rest_api:stagingfolder-list')


class StagingFolderFileAPIViewTestMixin:
    def _request_test_staging_folder_file_delete_api_view(self):
        return self.delete(
            viewname='rest_api:stagingfolderfile-detail', kwargs={
                'staging_folder_pk': self.test_staging_folder.pk,
                'encoded_filename': self.test_staging_folder_file.encoded_filename
            }
        )

    def _request_test_staging_folder_file_detail_api_view(self):
        return self.get(
            viewname='rest_api:stagingfolderfile-detail', kwargs={
                'staging_folder_pk': self.test_staging_folder.pk,
                'encoded_filename': self.test_staging_folder_file.encoded_filename
            }
        )

    def _request_test_staging_folder_file_upload_api_view(self):
        return self.post(
            viewname='rest_api:stagingfolderfile-upload', kwargs={
                'staging_folder_pk': self.test_staging_folder.pk,
                'encoded_filename': self.test_staging_folder_file.encoded_filename
            }, data={'document_type': self.test_document_type.pk}
        )


class StagingFolderTestMixin(SourceTestMixin):
    def setUp(self):
        super().setUp()
        self.test_staging_folders = []

    def tearDown(self):
        for test_staging_folder in self.test_staging_folders:
            #fs_cleanup(filename=test_staging_folder.folder_path)
            shutil.rmtree(
                path=test_staging_folder.get_backend_data()['folder_path']
            )
            self.test_staging_folders.remove(test_staging_folder)

        super().tearDown()

    def _copy_test_document_to_test_staging_folder(self):
        shutil.copy(
            src=TEST_SMALL_DOCUMENT_PATH,
            dst=self.test_source.get_backend_data()['folder_path']
        )
        self.test_staging_folder_file = list(
            self.test_source.get_backend_instance().get_files()
        )[0]

    def _create_test_staging_folder(self, extra_data=None):
        backend_data = {
            'folder_path': mkdtemp(),
            'preview_width': TEST_STAGING_PREVIEW_WIDTH,
            'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=SourceBackendStagingFolder.get_class_path(),
            backend_data=backend_data
        )
        self.test_staging_folders.append(self.test_source)


class StagingFolderViewTestMixin:
    def _request_test_staging_file_delete_view(self, staging_folder, staging_file):
        return self.post(
            viewname='sources:staging_file_delete', kwargs={
                'staging_folder_id': staging_folder.pk,
                'encoded_filename': staging_file.encoded_filename
            }
        )
