from mock import call
from nose.tools import istest

from provy.more.debian import AptitudeRole, MySQLRole
from tests.unit.tools.helpers import ProvyTestCase


FOO_DB_WITH_JOHN_GRANTS = """
*************************** 1. row ***************************
Grants for john@%: GRANT USAGE ON *.* TO 'john'@'%' IDENTIFIED BY PASSWORD '*B9EE00DF55E7C816911C6DA56F1E3A37BDB31093'
*************************** 2. row ***************************
Grants for john@%: GRANT ALL PRIVILEGES ON `foo`.* TO 'john'@'%'
"""
FOO_DB_WITHOUT_JOHN_GRANTS = """
*************************** 1. row ***************************
Grants for john@%: GRANT USAGE ON *.* TO 'john'@'%' IDENTIFIED BY PASSWORD '*B9EE00DF55E7C816911C6DA56F1E3A37BDB31093'
"""
HOSTS_FOR_USER = """
*************************** 1. row ***************************
Host: 127.0.0.1
*************************** 2. row ***************************
Host: ::1
*************************** 3. row ***************************
Host: my-desktop
*************************** 4. row ***************************
Host: localhost
"""


class MySQLRoleTest(ProvyTestCase):
    def setUp(self):
        self.role = MySQLRole(prov=None, context={})

    @istest
    def has_no_grant_if_not_granted(self):
        with self.execute_mock() as execute:
            execute.return_value = FOO_DB_WITHOUT_JOHN_GRANTS
            self.assertFalse(self.role.has_grant('ALL', 'foo', 'john', '%', False))

    @istest
    def has_grant_if_granted(self):
        with self.execute_mock() as execute:
            execute.return_value = FOO_DB_WITH_JOHN_GRANTS
            self.assertTrue(self.role.has_grant('ALL', 'foo', 'john', '%', False))

    @istest
    def has_grant_if_granted_even_if_provided_full(self):
        with self.execute_mock() as execute:
            execute.return_value = FOO_DB_WITH_JOHN_GRANTS
            self.assertTrue(self.role.has_grant('ALL PRIVILEGES', 'foo', 'john', '%', False))

    @istest
    def has_grant_if_granted_even_if_provided_as_lowercase_string(self):
        with self.execute_mock() as execute:
            execute.return_value = FOO_DB_WITH_JOHN_GRANTS
            self.assertTrue(self.role.has_grant('all', 'foo', 'john', '%', False))

    @istest
    def can_get_user_grants(self):
        with self.execute_mock() as execute:
            execute.return_value = FOO_DB_WITHOUT_JOHN_GRANTS
            expected = ["GRANT USAGE ON *.* TO 'john'@'%' IDENTIFIED BY PASSWORD '*B9EE00DF55E7C816911C6DA56F1E3A37BDB31093'"]
            self.assertEqual(expected, self.role.get_user_grants('john', '%'))

    @istest
    def installs_necessary_packages_to_provision(self):
        with self.using_stub(AptitudeRole) as mock_aptitude, self.execute_mock() as execute:
            mock_aptitude.ensure_package_installed.return_value = 'some result'

            self.role.provision()

            self.assertEqual(execute.mock_calls, [
                call('echo "mysql-server mysql-server/root_password select temppass" | debconf-set-selections',
                     stdout=False, sudo=True),
                call('echo "mysql-server mysql-server/root_password_again select temppass" | debconf-set-selections',
                     stdout=False, sudo=True),
                call("mysqladmin -u %s -p'temppass' password '%s'" % (self.role.mysql_root_user, self.role.mysql_root_pass),
                     stdout=False, sudo=True),
            ])
            self.assertEqual(mock_aptitude.ensure_package_installed.mock_calls, [
                call('mysql-server'),
                call('mysql-client'),
                call('libmysqlclient-dev'),
            ])

    @istest
    def installs_necessary_packages_to_provision_again(self):
        with self.using_stub(AptitudeRole) as mock_aptitude, self.execute_mock() as execute:
            mock_aptitude.ensure_package_installed.return_value = False

            self.role.provision()

            self.assertEqual(execute.mock_calls, [
                call('echo "mysql-server mysql-server/root_password select temppass" | debconf-set-selections',
                     stdout=False, sudo=True),
                call('echo "mysql-server mysql-server/root_password_again select temppass" | debconf-set-selections',
                     stdout=False, sudo=True),
            ])
            self.assertEqual(mock_aptitude.ensure_package_installed.mock_calls, [
                call('mysql-server'),
                call('mysql-client'),
                call('libmysqlclient-dev'),
            ])

    @istest
    def gets_user_hosts(self):
        with self.execute_mock() as execute:
            execute.return_value = HOSTS_FOR_USER

            hosts = self.role.get_user_hosts('root')

            self.assertEqual(hosts, [
                '127.0.0.1',
                '::1',
                'my-desktop',
                'localhost',
            ])
            execute.assert_called_with('''mysql -u root -E -e "select Host from mysql.user where LOWER(User)='root'" mysql''',
                                       sudo=True, stdout=False)

    @istest
    def gets_user_hosts_using_password(self):
        with self.execute_mock() as execute:
            execute.return_value = HOSTS_FOR_USER
            self.role.mysql_root_pass = 'mypass'

            hosts = self.role.get_user_hosts('root')

            self.assertEqual(hosts, [
                '127.0.0.1',
                '::1',
                'my-desktop',
                'localhost',
            ])
            execute.assert_called_with('''mysql -u root --password="mypass" -E -e "select Host from mysql.user where LOWER(User)='root'" mysql''',
                                       sudo=True, stdout=False)
