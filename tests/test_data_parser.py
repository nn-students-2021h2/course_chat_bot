# -*- coding: utf-8 -*-
from io import StringIO
import unittest
from unittest import mock
from unittest.mock import patch

from data_parser import DataParser


class TestsDataParser(unittest.TestCase):

    def setUp(self) -> None:
        self.data_parser = DataParser()

    def test_serialize_data_file_exist(self):
        with patch('data_parser.os.path.exists') as mock_path:
            mock_path.return_value = True
            self.assertEqual(self.data_parser.serialize_data(), None)

    def test_serialize_data_file_ok_request(self):
        mock_open_handler = mock.mock_open()
        with patch('data_parser.open', mock_open_handler):
            with patch('data_parser.os.path.exists') as mock_path, patch('data_parser.requests.get') as mock_get:
                mock_get.return_value.ok = True
                mock_path.return_value = False
                self.data_parser.serialize_data()
        mock_open_handler.assert_called_with(self.data_parser.path_to_file, 'wb')

    def test_serialize_data_file_exception_request(self):
        with patch('data_parser.os.path.exists') as mock_path, patch('data_parser.requests.get') as mock_get,\
                patch('sys.stdout', new=StringIO()) as mock_out:
            mock_get.side_effect = Exception('qqq exception')
            mock_path.return_value = False
            self.data_parser.serialize_data()
        self.assertEqual(mock_out.getvalue().strip(), 'Error occurred: qqq exception')

    def test_retrieve_no_top_five(self):
        mock_open_handler = mock.mock_open()
        with patch('data_parser.open', mock_open_handler), patch.object(DataParser, 'serialize_data') as mock_data, \
                patch('data_parser.csv.DictReader') as mock_csv:
            mock_data.return_value = None
            mock_csv.return_value = [{'Confirmed': 1}, {'Confirmed': 2}]
            top_five = self.data_parser.retrieve_top_five()
            mock_open_handler.assert_called_with(self.data_parser.path_to_file, newline='')
        self.assertEqual(len(top_five), 2)

    def test_retrieve_top_five(self):
        mock_open_handler = mock.mock_open()
        with patch('data_parser.open', mock_open_handler), patch.object(DataParser, 'serialize_data') as mock_data, \
                patch('data_parser.csv.DictReader') as mock_csv:
            mock_data.return_value = None
            mock_csv.return_value = [{'Confirmed': 1}, {'Confirmed': 2}, {'Confirmed': 3}, {'Confirmed': 4},
                                     {'Confirmed': 5}, {'Confirmed': 6}]
            top_five = self.data_parser.retrieve_top_five()
            mock_open_handler.assert_called_with(self.data_parser.path_to_file, newline='')
        self.assertEqual(len(top_five), 5)

    def test_retrieve_all(self):
        mock_open_handler = mock.mock_open()
        with patch('data_parser.open', mock_open_handler), patch.object(DataParser, 'serialize_data') as mock_data, \
                patch('data_parser.csv.DictReader') as mock_csv:
            mock_data.return_value = None
            mock_csv.return_value = [{'Confirmed': 1}, {'Confirmed': 2}, {'Confirmed': 3}, {'Confirmed': 4},
                                     {'Confirmed': 5}, {'Confirmed': 6}]
            output = self.data_parser.retrieve_all()
            mock_open_handler.assert_called_with(self.data_parser.path_to_file, newline='')
        self.assertEqual(len(output), 6)


if __name__ == '__main__':
    unittest.main()
