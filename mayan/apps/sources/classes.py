import logging

from django.apps import apps
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from django.core.files import File
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.functional import cached_property

from mayan.apps.common.class_mixins import AppsModuleLoaderMixin
from mayan.apps.converter.classes import ConverterBase
from mayan.apps.converter.transformations import TransformationResize
from mayan.apps.storage.classes import DefinedStorage

from .literals import STORAGE_NAME_SOURCE_CACHE_FOLDER

logger = logging.getLogger(name=__name__)


class DocumentCreateWizardStep(AppsModuleLoaderMixin):
    _deregistry = {}
    _loader_module_name = 'wizard_steps'
    _registry = {}

    @classmethod
    def deregister(cls, step):
        cls._deregistry[step.name] = step

    @classmethod
    def deregister_all(cls):
        for step in cls.get_all():
            cls.deregister(step=step)

    @classmethod
    def done(cls, wizard):
        return {}

    @classmethod
    def get(cls, name):
        for step in cls.get_all():
            if name == step.name:
                return step

    @classmethod
    def get_all(cls):
        return sorted(
            [
                step for step in cls._registry.values() if step.name not in cls._deregistry
            ], key=lambda x: x.number
        )

    @classmethod
    def get_choices(cls, attribute_name):
        return [
            (step.name, getattr(step, attribute_name)) for step in cls.get_all()
        ]

    @classmethod
    def get_form_initial(cls, wizard):
        return {}

    @classmethod
    def get_form_kwargs(cls, wizard):
        return {}

    @classmethod
    def post_upload_process(cls, document, query_string=None):
        for step in cls.get_all():
            step.step_post_upload_process(
                document=document, query_string=query_string
            )

    @classmethod
    def register(cls, step):
        if step.name in cls._registry:
            raise Exception('A step with this name already exists: %s' % step.name)

        if step.number in [reigstered_step.number for reigstered_step in cls.get_all()]:
            raise Exception('A step with this number already exists: %s' % step.name)

        cls._registry[step.name] = step

    @classmethod
    def reregister(cls, name):
        cls._deregistry.pop(name)

    @classmethod
    def reregister_all(cls):
        cls._deregistry = {}

    @classmethod
    def step_post_upload_process(cls, document, query_string=None):
        pass


class PseudoFile(File):
    def __init__(self, file, name):
        self.name = name
        self.file = file
        self.file.seek(0, os.SEEK_END)
        self.size = self.file.tell()
        self.file.seek(0)


class SourceBackendMetaclass(type):
    _registry = {}

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(
            mcs, name, bases, attrs
        )
        if not new_class.__module__ == 'mayan.apps.sources.classes':
            mcs._registry[
                '{}.{}'.format(new_class.__module__, name)
            ] = new_class

        return new_class


class SourceBackendBase(AppsModuleLoaderMixin):
    """
    Base class for the source backends.

    The fields attribute is a list of dictionaries with the format:
    {
        'name': ''  # Field internal name
        'label': ''  # Label to show to users
        'initial': ''  # Field initial value
        'default': ''  # Default value.
    }
    """
    fields = {}


class SourceBackend(
    six.with_metaclass(SourceBackendMetaclass, SourceBackendBase)
):
    _loader_module_name = 'source_backends'
    upload_form_class = None

    @classmethod
    def post_load_modules(cls):
        for name, source_backend in cls.get_all().items():
            source_backend.intialize()

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def get_all(cls):
        return cls._registry

    @classmethod
    def get_choices(cls):
        return sorted(
            [
                (
                    key, backend.label
                ) for key, backend in cls.get_all().items()
            ], key=lambda x: x[1]
        )

    @classmethod
    def get_class_path(cls):
        for path, klass in cls.get_all().items():
            if klass is cls:
                return path

    @classmethod
    def get_upload_form_class(cls):
        return cls.upload_form_class

    @classmethod
    def get_setup_form_schema(cls):
        result = {
            'fields': cls.fields,
            'widgets': getattr(cls, 'widgets', {})
        }
        if hasattr(cls, 'field_order'):
            result['field_order'] = cls.field_order
        else:
            result['field_order'] = ()

        return result

    @classmethod
    def intialize(cls):
        return

    def __init__(self, model_instance_id, **kwargs):
        self.model_instance_id = model_instance_id
        self.kwargs = kwargs

    def create(self):
        """
        Called after the source model's .save() method for new
        instances.
        """
        return

    def delete(self):
        """
        Called before the source model's .delete() method.
        """
        return

    def get_model_instance(self):
        Source = apps.get_model(app_label='sources', model_name='Source')
        return Source.objects.get(pk=self.model_instance_id)

    def get_task_extra_kwargs(self):
        return {}

    def get_view_context(self, context, request):
        return {}

    def process_document(self, **kwargs):
        raise NotImplementedError(
            '%(cls)s is missing the method `process_document`.' % {
                'cls': self.__class__.__name__
            }
        )

    def save(self):
        """
        Called after the source model's .save() method for existing
        instances.
        """
        return


class SourceBackendNull(SourceBackend):
    label = _('Null backend')
