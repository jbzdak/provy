from provy.core import Role


class SudoRole(Role):

    """
        Role that manages sudoers file.
    """

    def _upload_sudoers(self, local_file):
        tmpdir = self.create_remote_temp_dir(owner="root", chmod="440")
        self.change_path_owner(tmpdir, "root")
        remote_name = tmpdir + "/sudoers"
        self.put_file(local_file, remote_name, sudo=True, stdout=False)
        return remote_name

    def check_sudoers(self, local_file):
        """
        Uploads `local_file` to remote server, checks it for correct syntax and
        returns uploaded file name.

        :param local_file: Path of local file to be checked for validity on
        remote system.

        :return: Path to uploaded version of sudoers file on remote server. This
         will be in `/tmp` directory.
        """
        remote_name = self._upload_sudoers(local_file)
        self.execute("visudo -c -f {}".format(remote_name), sudo=True,
                     stdout=False)
        return remote_name

    def upload_sudoers(self, local_file):
        """
        Uploads `local_file` to remote server, checks it for correct syntax and
        if format is correct it replaces sudoers file.

        :param local_file: Path of local file to be checked for validity on
        remote system.
        """
        remote_name = self.check_sudoers(local_file)
        #Must be a single command, otherwise /etc/sudoers will end up broken.
        self.execute("mv {} /etc/sudoers && chmod 440 /etc/sudoers && chown root:root /etc/sudoers".format(remote_name), sudo=True)
