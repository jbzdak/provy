# -*- coding: utf-8 -*-


from hashlib import md5
import json
import os

from .base import Synchronizer, BaseSynchronizeRole
from .local_synchronizer import LocalSynchronizer, BaseLocalSynchronizeRole

class VersionSynchronizer(LocalSynchronizer):


    def __init__(self, role, current_version, local_path, remote_path, recursive, debug, min_version = None):
        super(VersionSynchronizer, self).__init__(role, local_path, remote_path,
                                                  recursive, debug)
        self.current_version = current_version
        if min_version is None:
            self.min_version = self.current_version

    def get_manifest_contents_for_current_dir(self):
        return json.dumps({'version': self.current_version})


    def has_changes(self):
        manifest = self._load_manifest_file()
        if manifest is None:
            return True
        try:
            manifest = json.loads(manifest)
            version = manifest['version']
        except (TypeError, AttributeError, KeyError, ValueError) as e:

            if self.debug:
                print (manifest)
                print(e)
            return True
        try:
            return version < self.min_version
        except (AttributeError, ValueError) as e:
            return True


class VersionSynchronizeRole(BaseLocalSynchronizeRole):

    def synchronize_path(self, version, local_path, remote_path, recursive=True, debug=False, min_version=None):
        sync = VersionSynchronizer(self, version, local_path, remote_path, recursive=recursive, debug=debug, min_version=min_version)
        sync.validate()
        sync.execute()

