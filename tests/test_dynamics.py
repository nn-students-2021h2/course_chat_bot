# -*- coding: utf-8 -*-
import unittest
from unittest import mock
from unittest.mock import patch

from data_parser import DataParser
from dynamics import DiseaseDynamics


class TestsDynamics(unittest.TestCase):

    def setUp(self) -> None:
        self.dynamics = DiseaseDynamics()
        self.data_parser = DataParser()

    def test_find_record_none(self):
        stats = [{'Country_Region': 'test1_coutry', 'Province_State': 'test_state'},
                 {'Country_Region': 'test2_coutry', 'Province_State': 'test_state'}]
        test_province = {'Country_Region': 'test_coutry', 'Province_State': 'test_state'}
        record = self.dynamics.find_record(test_province, stats)
        self.assertEqual(record, None)

    def test_find_record_true(self):
        stats = [{'Country_Region': 'test1_coutry', 'Province_State': 'test_state'},
                 {'Country_Region': 'test2_coutry', 'Province_State': 'test_state'}]
        test_province = {'Country_Region': 'test1_coutry', 'Province_State': 'test_state'}
        record = self.dynamics.find_record(test_province, stats)
        self.assertEqual(record, test_province)

    def test_find_record_false(self):
        stats = [{'Country_Region': 'test1_coutry', 'Province_State': 'test_state'},
                 {'Country_Region': 'test2_coutry', 'Province_State': 'test_state'}]
        test_province = {'Country_Region': 'test3_coutry', 'Province_State': 'test_state'}
        record = self.dynamics.find_record(test_province, stats)
        self.assertEqual(record, None)

    def test_find_record_diff_state(self):
        stats = [{'Country_Region': 'test1_coutry', 'Province_State': 'test_state'},
                 {'Country_Region': 'test2_coutry', 'Province_State': 'test_state'}]
        test_province = {'Country_Region': 'test1_coutry', 'Province_State': 'test_state_new'}
        record = self.dynamics.find_record(test_province, stats)
        self.assertEqual(record, None)

    def test_get_top_five_smaller(self):
        with patch.object(DiseaseDynamics, 'get_disease_dynamic') as mock_dynamics:
            mock_dynamics.return_value = [{'Dynamic': 1, 'Country': '1', 'State': '1', 'Confirmed': '1'},
                                          {'Dynamic': 2, 'Country': '2', 'State': '2', 'Confirmed': '2'}]
            msg = self.dynamics.get_top_five()
        self.assertEqual(msg, '2, 2: 2 (+2)\n1, 1: 1 (+1)\n')

    def test_get_top_five_none(self):
        with patch.object(DiseaseDynamics, 'get_disease_dynamic') as mock_dynamics:
            mock_dynamics.return_value = []
            msg = self.dynamics.get_top_five()
        self.assertEqual(msg, '')

    def test_get_top_five_bigger(self):
        with patch.object(DiseaseDynamics, 'get_disease_dynamic') as mock_dynamics:
            mock_dynamics.return_value = [{'Dynamic': 1, 'Country': '1', 'State': '1', 'Confirmed': '1'},
                                          {'Dynamic': 2, 'Country': '2', 'State': '2', 'Confirmed': '2'},
                                          {'Dynamic': 3, 'Country': '3', 'State': '3', 'Confirmed': '3'},
                                          {'Dynamic': 4, 'Country': '4', 'State': '4', 'Confirmed': '4'},
                                          {'Dynamic': 5, 'Country': '5', 'State': '5', 'Confirmed': '5'},
                                          {'Dynamic': 6, 'Country': '6', 'State': '6', 'Confirmed': '6'},
                                          ]
            msg = self.dynamics.get_top_five()
        self.assertEqual(msg, '6, 6: 6 (+6)\n5, 5: 5 (+5)\n4, 4: 4 (+4)\n3, 3: 3 (+3)\n2, 2: 2 (+2)\n')

    def test_get_disease_dynamic(self):
        mock_open_handler = mock.mock_open()
        with patch('data_parser.open', mock_open_handler):
            dynamic = self.dynamics.get_disease_dynamic()
        self.assertIsNot(dynamic, [])

    @patch.object(DataParser, 'retrieve_all', return_value=[])
    def test_get_disease_dynamic_none(self, mock_data):
        mock_open_handler = mock.mock_open()
        with patch('data_parser.open', mock_open_handler):
            dynamic = self.dynamics.get_disease_dynamic()
        self.assertEqual(dynamic, [])


if __name__ == '__main__':
    unittest.main()
