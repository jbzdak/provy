# -*- coding: utf-8 -*-


import abc
import os
from provy.core import Role
__all__ = ['RsyncSynchronize']


class BaseSynchronizeRole(Role):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def synchronize_path(self, local_path, remote_path, recursive=True, debug=False):
        pass

    @abc.abstractmethod
    def _install_synchronize_packages(self):
        pass

    def provision(self):
        super(BaseSynchronizeRole, self).provision()
        self._install_synchronize_packages()

class Synchronizer(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, role, local_path, remote_path, recursive, debug):
        self.role = role
        self.local_path = local_path
        self.remote_path = remote_path
        self.recursive = recursive
        self.debug = debug

    @abc.abstractmethod
    def execute(self):
        pass

    @abc.abstractmethod
    def validate(self):
        if os.path.isdir(self.local_path) and not self.recursive:
            raise ValueError("You try to synchronize directory without specyfying recursive parameter.")
