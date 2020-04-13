# -*- coding: utf-8 -*-
from io import StringIO
import unittest
from unittest import mock
from unittest.mock import patch

from chat_bot import LOG_ACTIONS, get_data_from_site, get_most_upvoted_fact, log_action, write_history


@log_action
def simple_action(update):
    return None


LOG_VALUES = [{'user': '1',
               'function': 'func1',
               'message': 'test message',
               },
              {'user': '2',
               'function': 'func1',
               'message': 'test message',
               },
              {'user': '2',
               'function': 'func1',
               'message': 'test message',
               },
              ]


class TestsLogs(unittest.TestCase):

    def setUp(self) -> None:
        self.update = mock.MagicMock()

    def tearDown(self) -> None:
        global LOG_ACTIONS
        LOG_ACTIONS = []

    def test_log_action(self):
        self.update.message.text = 'bla-bla'
        self.update.effective_user.first_name = 'Super Name'

        simple_action(self.update)
        self.assertEqual(LOG_ACTIONS, [{'user': 'Super Name', 'function': 'simple_action', 'message': 'bla-bla'}])

    def test_no_message_attr(self):
        self.update = mock.MagicMock(spec=['effective_user'])

        simple_action(self.update)
        self.assertEqual(LOG_ACTIONS, [])

    def test_no_user_attr(self):
        self.update = mock.MagicMock(spec=['message'])

        simple_action(self.update)
        self.assertEqual(LOG_ACTIONS, [])

    def test_none_update(self):
        self.update = None

        simple_action(self.update)
        self.assertEqual(LOG_ACTIONS, [])

    def test_no_update(self):
        with self.assertRaises(IndexError):
            simple_action()


class TestsWriteHistory(unittest.TestCase):

    def setUp(self) -> None:
        self.update = mock.MagicMock()

    def test_file_name(self):
        mock_open_handler = mock.mock_open()
        with patch('chat_bot.open', mock_open_handler):
            file_name, reply_text = write_history(self.update, 'new_file.txt', 2)
        mock_open_handler.assert_called_with('new_file.txt', 'w', encoding='utf-8')
        self.assertEqual(file_name, 'new_file.txt')

    def test_no_history(self):
        mock_open_handler = mock.mock_open()
        with patch('chat_bot.open', mock_open_handler):
            file_name, reply_text = write_history(self.update, 'new_file.txt', 2)

        self.assertEqual(reply_text, '')

    @patch('chat_bot.LOG_ACTIONS', LOG_VALUES)
    def test_write_history(self):
        self.update.effective_user.first_name = '2'
        mock_open_handler = mock.mock_open()
        with patch('chat_bot.open', mock_open_handler):
            file_name, reply_text = write_history(self.update, 'new_file.txt', 2)

        self.assertEqual(reply_text, '1 User: 2 Message: test message\n2 User: 2 Message: test message\n')

    @patch('chat_bot.LOG_ACTIONS', LOG_VALUES)
    def test_write_history_no_user(self):
        self.update.effective_user.first_name = 'no_such_user'
        mock_open_handler = mock.mock_open()
        with patch('chat_bot.open', mock_open_handler):
            file_name, reply_text = write_history(self.update, 'new_file.txt', 2)

        self.assertEqual(reply_text, '')


class TestsFacts(unittest.TestCase):

    def test_bad_request(self):
        with patch('chat_bot.requests.get') as mock_get:
            mock_get.return_value.ok = False
            data = get_data_from_site('http://qqq.com')
        self.assertEqual(data, None)

    def test_ok_request(self):
        with patch('chat_bot.requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {'cat': 1}
            data = get_data_from_site('http://qqq.com')
        self.assertEqual(data, {'cat': 1})

    def test_exception_request(self):
        with patch('chat_bot.requests.get') as mock_get, patch('sys.stdout', new=StringIO()) as mock_out:
            mock_get.side_effect = Exception('qqq exception')
            get_data_from_site('http://google.com')
        self.assertEqual(mock_out.getvalue().strip(), 'Error occurred: qqq exception')

    def test_get_facts_no_data(self):
        with patch('chat_bot.get_data_from_site') as mock_data:
            mock_data.return_value = None
            most_upvoted = get_most_upvoted_fact()
        self.assertEqual(most_upvoted, '[ERR] Could not retrieve most upvoted fact')

    def test_get_facts_no_most_upvoted(self):
        with patch('chat_bot.get_data_from_site') as mock_data:
            mock_data.return_value = {'all': [{'upvotes': 0, 'text': 'text message'}]}
            most_upvoted = get_most_upvoted_fact()
        self.assertEqual(most_upvoted, '[ERR] Could not retrieve most upvoted fact')

    def test_get_facts_most_upvoted(self):
        with patch('chat_bot.get_data_from_site') as mock_data:
            mock_data.return_value = {'all': [{'upvotes': 1, 'text': 'text message'}]}
            most_upvoted = get_most_upvoted_fact()
        self.assertEqual(most_upvoted, 'text message')


if __name__ == '__main__':
    unittest.main()
