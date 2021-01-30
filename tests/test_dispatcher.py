from datetime import datetime
from unittest import TestCase
from unittest.mock import ANY
from dispatcher import dispatcher


# import re
#
# date_re = re.compile('^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$')


class TestDispatcher(TestCase):

    def test_dispatcher(self):
        city_list = ['Москва', 'Питер']

        expected_dictionary = {'Москва': {'Питер': [[ANY, ANY],
                                                    [ANY, ANY],
                                                    [ANY, ANY],
                                                    [ANY, ANY],
                                                    [ANY, ANY]]},
                               'Питер': {'Москва': [[ANY, ANY],
                                                    [ANY, ANY],
                                                    [ANY, ANY],
                                                    [ANY, ANY],
                                                    [ANY, ANY]]}}
        dispatcher_test = dispatcher(city_list)
        self.assertEqual(dispatcher_test, expected_dictionary)
