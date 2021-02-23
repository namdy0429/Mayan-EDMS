import json
import shutil

from django.db.models import Q

from mayan.apps.documents.literals import DOCUMENT_FILE_ACTION_PAGES_NEW
from mayan.apps.documents.tests.literals import (
    TEST_DOCUMENT_DESCRIPTION, TEST_SMALL_DOCUMENT_PATH
)
from mayan.apps.storage.utils import fs_cleanup, mkdtemp

from ..forms import NewDocumentForm
from ..models import Source
from ..source_backends.email_backends import (
    SourceBackendIMAPEmail, SourceBackendPOP3Email
)
from ..source_backends.literals import (
    DEFAULT_EMAIL_IMAP_MAILBOX, DEFAULT_EMAIL_IMAP_SEARCH_CRITERIA,
    DEFAULT_EMAIL_IMAP_STORE_COMMANDS, DEFAULT_EMAIL_METADATA_ATTACHMENT_NAME,
    DEFAULT_EMAIL_POP3_TIMEOUT, DEFAULT_PERIOD_INTERVAL,
    SOURCE_UNCOMPRESS_CHOICE_NEVER
)
from ..source_backends.staging_folder_backends import SourceBackendStagingFolder
from ..source_backends.watch_folder_backends import SourceBackendWatchFolder
from ..source_backends.web_form_backends import SourceBackendWebForm

from .literals import (
    TEST_SOURCE_BACKEND_PATH, TEST_SOURCE_BACKEND_EMAIL_PATH,
    TEST_SOURCE_BACKEND_PERIODIC_PATH, TEST_SOURCE_LABEL,
    TEST_SOURCE_LABEL_EDITED
)

from .mocks import MockRequest


class DocumentFileUploadViewTestMixin:
    def _request_document_file_upload_view(self):
        with open(file=TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_object:
            return self.post(
                viewname='sources:document_file_upload', kwargs={
                    'document_id': self.test_document.pk,
                    'source_id': self.test_source.pk,
                }, data={
                    'document-action': DOCUMENT_FILE_ACTION_PAGES_NEW,
                    'source-file': file_object
                }
            )

    def _request_document_file_upload_no_source_view(self):
        with open(file=TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_object:
            return self.post(
                viewname='sources:document_file_upload', kwargs={
                    'document_id': self.test_document.pk,
                }, data={
                    'document-action': DOCUMENT_FILE_ACTION_PAGES_NEW,
                    'source-file': file_object
                }
            )


class DocumentUploadIssueViewTestMixin:
    def _request_test_source_create_view(self):
        return self.post(
            viewname='sources:source_create', kwargs={
                'source_type_name': SOURCE_CHOICE_WEB_FORM
            }, data={
                'enabled': True, 'label': 'test', 'uncompress': 'n'
            }
        )

    def _request_test_source_edit_view(self):
        return self.post(
            viewname='documents:document_properties_edit', kwargs={
                'document_id': self.test_document.pk
            },
            data={
                'description': TEST_DOCUMENT_DESCRIPTION,
                'label': self.test_document.label,
                'language': self.test_document.language
            }
        )


class DocumentUploadWizardViewTestMixin:
    def _request_upload_wizard_view(self, document_path=TEST_SMALL_DOCUMENT_PATH):
        with open(file=document_path, mode='rb') as file_object:
            return self.post(
                viewname='sources:document_upload_interactive', kwargs={
                    'source_id': self.test_source.pk
                }, data={
                    'source-file': file_object,
                    'document_type_id': self.test_document_type.pk,
                }
            )

    def _request_upload_interactive_view(self):
        return self.get(
            viewname='sources:document_upload_interactive', data={
                'document_type_id': self.test_document_type.pk,
            }
        )


class SourceTestMixin:
    def _create_test_source(self, backend_path, backend_data=None):
        self.test_source = Source.objects.create(
            backend_path=backend_path,
            backend_data=json.dumps(obj=backend_data),
            label=TEST_SOURCE_LABEL
        )


class EmailSourceBackendTestMixin(SourceTestMixin):
    def _create_test_email_source_backend(self, extra_data=None):
        backend_data = {
            'document_type_id': self.test_document_type.pk,
            'from_metadata_type_id': None,
            'host': '',
            'interval': DEFAULT_PERIOD_INTERVAL,
            'metadata_attachment_name': DEFAULT_EMAIL_METADATA_ATTACHMENT_NAME,
            'password': '',
            'port': '',
            'ssl': True,
            'subject_metadata_type_id': None,
            'store_body': False,
            'username': ''
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=TEST_SOURCE_BACKEND_EMAIL_PATH,
            backend_data=backend_data
        )


class IMAPEmailSourceTestMixin(SourceTestMixin):
    def _create_test_imap_email_source(self, extra_data=None):
        backend_data = {
            'document_type_id': self.test_document_type.pk,
            'execute_expunge': True,
            'from_metadata_type_id': None,
            'host': '',
            'interval': DEFAULT_PERIOD_INTERVAL,
            'mailbox': DEFAULT_EMAIL_IMAP_MAILBOX,
            'mailbox_destination': '',
            'metadata_attachment_name': DEFAULT_EMAIL_METADATA_ATTACHMENT_NAME,
            'password': '',
            'port': '',
            'search_criteria': DEFAULT_EMAIL_IMAP_SEARCH_CRITERIA,
            'ssl': True,
            'store_body': False,
            'store_commands': DEFAULT_EMAIL_IMAP_STORE_COMMANDS,
            'subject_metadata_type_id': None,
            'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER,
            'username': ''
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=SourceBackendIMAPEmail.get_class_path(),
            backend_data=backend_data
        )


class InteractiveSourceBackendTestMixin:
    class MockSourceForm:
        def __init__(self, **kwargs):
            self.cleaned_data = kwargs

    def setUp(self):
        super().setUp()
        self.test_document_form = self.get_test_document_form()

    def get_test_document_form(self):
        document_form = NewDocumentForm(
            data={}, document_type=self.test_document_type
        )
        document_form.full_clean()

        return document_form

    def get_test_request(self):
        return MockRequest(user=self._test_case_user)


class PeriodicSourceBackendTestMixin(SourceTestMixin):
    def _create_test_periodic_source_backend(self, extra_data=None):
        backend_data = {
            'interval': DEFAULT_PERIOD_INTERVAL
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=TEST_SOURCE_BACKEND_PERIODIC_PATH,
            backend_data=backend_data
        )


class POP3EmailSourceTestMixin(SourceTestMixin):
    def _create_test_pop3_email_source(self, extra_data=None):
        backend_data = {
            'document_type_id': self.test_document_type.pk,
            'from_metadata_type_id': None,
            'host': '',
            'interval': DEFAULT_PERIOD_INTERVAL,
            'metadata_attachment_name': DEFAULT_EMAIL_METADATA_ATTACHMENT_NAME,
            'password': '',
            'port': '',
            'ssl': True,
            'store_body': False,
            'subject_metadata_type_id': None,
            'timeout': DEFAULT_EMAIL_POP3_TIMEOUT,
            'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER,
            'username': ''
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=SourceBackendPOP3Email.get_class_path(),
            backend_data=backend_data
        )


class SourceViewTestMixin:
    def _request_test_source_backend_selection_view(self):
        return self.get(
            viewname='sources:source_backend_selection'
        )

    def _request_test_source_create_view(
        self, backend_path=None, extra_data=None
    ):
        pk_list = list(Source.objects.values_list('pk', flat=True))

        data = {
            'enabled': True,
            'label': TEST_SOURCE_LABEL,
            'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER
        }

        if extra_data:
            data.update(extra_data)

        response = self.post(
            kwargs={
                'backend_path': backend_path or TEST_SOURCE_BACKEND_PATH
            }, viewname='sources:source_create', data=data
        )

        try:
            self.test_source = Source.objects.get(~Q(pk__in=pk_list))
        except Source.DoesNotExist:
            self.test_source = None

        return response

    def _request_test_source_delete_view(self):
        return self.post(
            viewname='sources:source_delete', kwargs={
                'source_id': self.test_source.pk
            }
        )

    def _request_test_source_edit_view(self):
        return self.post(
            viewname='sources:source_edit', kwargs={
                'source_id': self.test_source.pk
            }, data={
                'label': TEST_SOURCE_LABEL_EDITED,
                'uncompress': self.test_source.get_backend_data().get(
                    'uncompress'
                )
            }
        )

    def _request_test_source_list_view(self):
        return self.get(viewname='sources:source_list')

    def _request_test_source_test_get_view(self):
        return self.get(
            viewname='sources:source_test', kwargs={
                'source_id': self.test_source.pk
            }
        )

    def _request_test_source_test_post_view(self):
        return self.post(
            viewname='sources:source_test', kwargs={
                'source_id': self.test_source.pk
            }
        )


class EmailSourceBackendViewTestMixin(SourceViewTestMixin):
    def _request_test_email_source_create_view(self, extra_data=None):
        data = {
            'document_type_id': self.test_document_type.pk,
            'host': '127.0.0.1',
            'interval': DEFAULT_PERIOD_INTERVAL,
            'metadata_attachment_name': DEFAULT_EMAIL_METADATA_ATTACHMENT_NAME,
            'port': '0',
            'ssl': True,
            'store_body': False,
            'username': 'username'
        }

        if extra_data:
            data.update(extra_data)

        return self._request_test_source_create_view(
            backend_path=TEST_SOURCE_BACKEND_EMAIL_PATH, extra_data=data
        )


class WatchFolderTestMixin(SourceTestMixin):
    def setUp(self):
        super().setUp()
        self.temporary_directory = mkdtemp()
        self.test_watch_folders = []

    def tearDown(self):
        shutil.rmtree(path=self.temporary_directory)
        super().tearDown()

    def _create_test_watchfolder(self, extra_data=None):
        backend_data = {
            'document_type_id': self.test_document_type.pk,
            'folder_path': self.temporary_directory,
            'include_subdirectories': False,
            'interval': DEFAULT_PERIOD_INTERVAL,
            'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=SourceBackendWatchFolder.get_class_path(),
            backend_data=backend_data
        )


class WebFormSourceTestMixin(SourceTestMixin):
    def _create_test_web_form_source(self, extra_data=None):
        backend_data = {'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER}

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=SourceBackendWebForm.get_class_path(),
            backend_data=backend_data
        )

        self.test_watch_folder = WatchFolderSource.objects.create(**kwargs)
        self.test_watch_folders.append(self.test_watch_folder)
