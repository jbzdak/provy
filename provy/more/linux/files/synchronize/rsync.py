# -*- coding: utf-8 -*-

from .base import Synchronizer, BaseSynchronizeRole

class RsyncSynchronizer(Synchronizer):

    def __init__(self, role, local_path, remote_path, recursive, debug,
                 additional_opts = None):
        super(RsyncSynchronizer, self).__init__(role, local_path, remote_path,
                                                recursive, debug)
        if additional_opts is None:
            additional_opts = []

        self.additional_opts = additional_opts

    def validate(self):
        super(RsyncSynchronizer, self).validate()
        self._assert_has_rsync_locally()

    def execute(self):
        super(RsyncSynchronizer, self).execute()
        self.role.execute_local(self._prepare_rsync_command(), stdout=self.debug)

    def _assert_has_rsync_locally(self):
        result = self.role.execute_local("which rsync | wc -l", stdout=False)
        has_rsync =  int(result) > 0

        if not has_rsync:
            raise ValueError("It seems that rsync is not installed locally, please install it before using RsyncSynchronize. ")

    @property
    def remote_path_with_host(self):
        return "{}:{}".format(self.role.context['__provy']['host_string'], self.remote_path)

    def _prepare_rsync_command(self):
        opts = ['-rl', '--delete']
        if self.debug:
            opts.append('-v')
        opts.extend(self.additional_opts)
        command = ['rsync'] + opts + [self.local_path, self.remote_path_with_host]

        return " ".join(command)

class RsyncSynchronizeRole(BaseSynchronizeRole):
    def synchronize_path(self, local_path, remote_path, recursive=True,
                         debug=False, additional_rsync_opts = tuple()):

        synchronizer = RsyncSynchronizer(self, local_path, remote_path, recursive, debug, additional_rsync_opts)
        synchronizer.validate()
        synchronizer.execute()
