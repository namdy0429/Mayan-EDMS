from django.conf.urls import url

from .api_views import (
    APIStagingSourceFileImageView, APIStagingSourceFileUploadView,
    APIStagingSourceFileView
)
from .views import StagingFileDeleteView

urlpatterns = [
    url(
        regex=r'^staging_folders/(?P<staging_folder_id>\d+)/files/(?P<encoded_filename>.+)/delete/$',
        name='staging_file_delete', view=StagingFileDeleteView.as_view()
    ),
]

api_urls = [
    url(
        regex=r'^staging_folders_files/(?P<staging_folder_pk>[0-9]+)/(?P<encoded_filename>.+)/image/$',
        name='stagingfolderfile-image',
        view=APIStagingSourceFileImageView.as_view()
    ),
    url(
        regex=r'^staging_folders_files/(?P<staging_folder_pk>[0-9]+)/(?P<encoded_filename>.+)/upload/$',
        name='stagingfolderfile-upload',
        view=APIStagingSourceFileUploadView.as_view()
    ),
    url(
        regex=r'^staging_folders_files/(?P<staging_folder_pk>[0-9]+)/(?P<encoded_filename>.+)/$',
        name='stagingfolderfile-detail',
        view=APIStagingSourceFileView.as_view()
    )
]
