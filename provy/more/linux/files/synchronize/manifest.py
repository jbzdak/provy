# -*- coding: utf-8 -*-
import os

from hashlib import md5

from .base import Synchronizer, BaseSynchronizeRole
from .local_synchronizer import LocalSynchronizer


def _build_file_manifest(local_path):
    file_manifest = []
    for root, dirs, files in os.walk(local_path):
        for f in files:
            file_manifest.append(os.path.join(root, f))
    return file_manifest

class ManifestSynchronizer(LocalSynchronizer):

    MANIFEST_FILE = ".manifest.json"

    def has_changes(self):
        manifest_file = self.__get_manifest_file()
        if manifest_file is None:
            return True

    def __get_manifest_file(self):
        return self.role.read_remote_file(self.remote_path+ '/' + self.MANIFEST_FILE)







