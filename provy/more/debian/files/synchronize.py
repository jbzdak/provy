# -*- coding: utf-8 -*-

from ...linux.files.synchronize import (
    RsyncSynchronizeRole as LinuxRsyncSynchronize,
    VersionSynchronizeRole as LinuxVersionSynchronizeRole)
from provy.more.debian.package.aptitude import AptitudeRole


class RsyncSynchronize(LinuxRsyncSynchronize):

    def _install_synchronize_packages(self):
        super(RsyncSynchronize, self)._install_synchronize_packages()
        with self.using(AptitudeRole) as role:
            role.ensure_package_installed("rsync")

class VersionSynchronizeRole(LinuxVersionSynchronizeRole):
    @property
    def OsBasedRsyncSynchronizer(self):
        return RsyncSynchronize