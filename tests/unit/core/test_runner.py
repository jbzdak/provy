from nose.tools import istest

from provy.core.errors import ConfigurationError
from tests.unit.tools.helpers import ProvyTestCase


class RunnerTest(ProvyTestCase):
    @istest
    def cannot_get_items_if_prov_doesnt_have_required_attribute(self):
        # self.assertRaises(ConfigurationError, get_items, 'some prov variable', 'inexistant_item_name', 'inexistant_item_key', 'some test func')
        pass