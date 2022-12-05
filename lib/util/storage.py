from django.core.files.storage import get_storage_class
from django.conf import settings
from django.utils.functional import LazyObject
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class FtpStorage(LazyObject):
    def _setup(self):
        self._wrapped = get_storage_class('storages.backends.ftp.FTPStorage')()

ftp_storage = FtpStorage()

def upload_image(file_dir, file_name, image_object):
    try:
        image_path = default_storage.save(
                f'{file_dir}/{file_name}', ContentFile(image_object.read()))
        image_url = settings.GS_URL + image_path
    except:
        file_dir = file_dir.replace("/", "_")
        image_path = ftp_storage.save(
                f'{file_dir}_{file_name}', ContentFile(image_object.read()))
        image_url = settings.BASE_URL + image_path
    print(image_url)
    return image_url