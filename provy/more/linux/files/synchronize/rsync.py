# -*- coding: utf-8 -*-

from .base import Synchronizer, BaseSynchronizeRole

class RsyncSynchronizer(Synchronizer):
    """
    Plain old rsync synchronizer.
    """

    def __init__(self, role, local_path, remote_path, recursive, debug,
                 additional_opts = None, login_as = None):
        super(RsyncSynchronizer, self).__init__(role, local_path, remote_path,
                                                recursive, debug)
        if additional_opts is None:
            additional_opts = []

        self.additional_opts = additional_opts
        self.remote_user = login_as

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
        remote_host = self.role.context['__provy']['current_server']['address']
        if self.remote_user:
            remote_user = self.remote_user
        else:
            remote_user = self.role.context['__provy']['current_server'].get('user', None)
        if remote_user is not None:
            remote_user += '@'
        return "{}{}:{}".format(remote_user, remote_host, self.remote_path)

    def _prepare_rsync_command(self):
        opts = ['-rl', '--delete']
        if self.debug:
            opts.append('-v')
        opts.extend(self.additional_opts)
        command = ['rsync'] + opts + [self.local_path, self.remote_path_with_host]

        return " ".join(command)

class RsyncSynchronizeRole(BaseSynchronizeRole):

    def synchronize_path(self, local_path, remote_path, recursive=True,
                         debug=False, additional_rsync_opts = tuple(), login_as=None):

        synchronizer = RsyncSynchronizer(self, local_path, remote_path, recursive, debug, additional_rsync_opts, login_as)
        synchronizer.validate()
        synchronizer.execute()
