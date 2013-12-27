# -*- coding: utf-8 -*-
from StringIO import StringIO
import abc
import os
from .base import Synchronizer, BaseSynchronizeRole

class BaseLocalSynchronizeRole(BaseSynchronizeRole):

    @property
    @abc.abstractmethod
    def OsBasedRsyncSynchronizer(self):
        raise ValueError()

    def _install_synchronize_packages(self):
        super(BaseLocalSynchronizeRole, self)._install_synchronize_packages()


class LocalSynchronizer(Synchronizer):

    MANIFEST_FILE = ".manifest.json"

    @abc.abstractmethod
    def has_changes(self):
        pass

    @abc.abstractmethod
    def get_manifest_contents_for_current_dir(self):
        pass

    def manifest_path(self):
        return "{}/{}".format(self.remote_path, self.MANIFEST_FILE)


    def _load_manifest_file(self):
        if not self.role.remote_exists(self.manifest_path()):
            return None
        return self.role.read_remote_file(self.manifest_path())

    def validate(self):
        super(LocalSynchronizer, self).validate()
        if not os.path.isdir(self.local_path):
            raise ValueError("Sorry this class ({}) does not support synchronizing paths (yet).")

    def execute(self):
        super(LocalSynchronizer, self).execute()
        changes = self.has_changes()
        if self.debug:
            if changes:
                print("Because of changes will synchronize local path '{}'".format(self.local_path))
            else:
                print("Local path '{}' unchanged".format(self.local_path))

        if changes:
            with self.role.using(self.role.OsBasedRsyncSynchronizer) as role:
                role.synchronize_path(
                    self.local_path, self.remote_path,
                    recursive=self.recursive, debug=self.debug)
            self.role.put_file(StringIO(self.get_manifest_contents_for_current_dir()), self.manifest_path())

