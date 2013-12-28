# -*- coding: utf-8 -*-

"""
The whole idea is that to streamline deployment you might want make decision
whether to synchronize without reading whole remote directory.

So we basically store some information on the remote side, that allows
us to make this decision faster.
"""

from StringIO import StringIO
import abc
import os
from .base import Synchronizer, BaseSynchronizeRole

class BaseLocalSynchronizeRole(BaseSynchronizeRole):

    @property
    @abc.abstractmethod
    def OsBasedRsyncSynchronizer(self):
        """
        If we need to synchronize we'll use Rsync role. This property returns
        rsync role for the proper OS.
        """
        raise ValueError()

    def synchronize_path(self, local_path, remote_path, recursive=True,
                         debug=False, login_as = None):

        super(BaseLocalSynchronizeRole, self).synchronize_path(local_path,
                                                               remote_path,
                                                               recursive, debug)
        self.login_as = None


    def _install_synchronize_packages(self):
        super(BaseLocalSynchronizeRole, self)._install_synchronize_packages()


class LocalSynchronizer(Synchronizer):

    """
    Base class for local synchronizers.

    Idea is that store magic file containing version information on remote side,
    we download only this file, to make decision whether to synchronize
    """

    MANIFEST_FILE = ".manifest.json"

    @abc.abstractmethod
    def has_changes(self):
        """
        If returns true we will use rsync to keep remote dir up to date.
        """
        pass

    @abc.abstractmethod
    def get_manifest_contents_for_current_dir(self):
        """
        Returns contens of manifest file, to be sent to remote server after
        synchronization
        :return: Returns contens of manifest file.
        :rtype: :class:`str`
        """
        pass

    def manifest_path(self):
        """
        Returns remote path to the manifest file.
        """
        return "{}/{}".format(self.remote_path, self.MANIFEST_FILE)


    def _load_manifest_file(self):
        """
        Returns contents of the manifest file on the remote server, or :class:`None`
        if it doesn't exist.
        """
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

