from django.utils.safestring import mark_safe

from mayan.apps.navigation.html_widgets import SourceColumnWidget

from .settings import (
    setting_preview_width, setting_preview_height, setting_thumbnail_width,
    setting_thumbnail_height
)


class ThumbnailWidget(SourceColumnWidget):
    container_class = '',
    gallery_name = ''
    template_name = 'documents/widgets/thumbnail.html'

    def disable_condition(self, instance):
        return True

    def get_extra_context(self):
        return {
            'container_class': self.container_class,
            'disable_title_link': self.disable_condition(instance=instance),
            'gallery_name': self.gallery_name,
            'instance': self.value,
            'size_preview_width': setting_preview_width.value,
            'size_preview_height': setting_preview_height.value,
            'size_thumbnail_width': setting_thumbnail_width.value,
            'size_thumbnail_height': setting_thumbnail_height.value,
        }


class BaseDocumentThumbnailWidget(ThumbnailWidget):
    container_class = '',
    gallery_name = 'document_list'

    def disable_condition(self, instance):
        # Disable the clickable link if the document is in the trash
        return instance.is_in_trash


def document_link(document):
    return mark_safe('<a href="%s">%s</a>' % (
        document.get_absolute_url(), document)
    )
