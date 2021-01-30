import json
from unittest import TestCase
from unittest.mock import patch, Mock, ANY

from vk_api.bot_longpoll import VkBotMessageEvent
from settings import DEFAULT_ANSWER
from bot import Bot


class TestBot(TestCase):
    RAW_EVENT = {
        'type': 'message_new',
        'object': {'message': {'date': 1610638250, 'from_id': 73049353, 'id': 58, 'out': 0, 'peer_id': 73049353,
                               'text': 'Приветик', 'conversation_message_id': 57, 'fwd_messages': [],
                               'important': False, 'random_id': 0, 'attachments': [], 'is_hidden': False}, },
        'group_id': 201430119, 'event_id': '4cdf16ecf8bf04771f4382a5e5f7833e9b41c772'}
    RUN_SCENARIO = {
        'type': 'message_new',
        'object': {'message': {'date': 1611234469, 'from_id': 73049353, 'id': 540,
                               'out': 0, 'peer_id': 73049353, 'text': '/ticket',
                               'conversation_message_id': 535, 'fwd_messages': [],
                               'important': False, 'random_id': 0, 'attachments': [], 'is_hidden': False}},
        'group_id': 201430119, 'event_id': 'e2817e8d72c2fb8d61020068e1ad0ab435db84b8'}

    def test_run(self):
        count = 5
        events = [{}] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('bot.vk_api.VkApi'):
            with patch('bot.vk_api.bot_longpoll.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.call_count = 5
                assert bot.on_event.call_count == count

    def test_on_event(self):
        event = VkBotMessageEvent(raw=self.RAW_EVENT)

        send_mock = Mock()
        with patch('bot.vk_api.VkApi'):
            with patch('bot.vk_api.bot_longpoll.VkBotLongPoll', ):
                bot = Bot('', '')
                bot.api = Mock()
                bot.api.messages.send = send_mock

                bot.on_event(event)

        send_mock.assert_called_once_with(
            message=DEFAULT_ANSWER,
            random_id=ANY,
            peer_id=self.RAW_EVENT['object']['message']['peer_id'], )

    def test_on_event_ticket(self):
        event = VkBotMessageEvent(raw=self.RUN_SCENARIO)

        send_mock = Mock()
        with patch('bot.vk_api.VkApi'):
            with patch('bot.vk_api.bot_longpoll.VkBotLongPoll', ):
                bot = Bot('', '')
                bot.api = Mock()
                bot.api.messages.send = send_mock

                bot.on_event(event)

        send_mock.assert_called_once_with(
            message="Для поиска билетов укажите город отправления",
            random_id=ANY,
            peer_id=self.RAW_EVENT['object']['message']['peer_id'], )

    def test_continue_scenario(self):
        step = {
            'text': 'Для поиска билетов укажите город отправления', 'fail_text': 'Данного города нет',
            'handler': 'handle_dispatch_city', 'next_step': 'step2'}
        text_to_send = step['fail_text']
        self.assertEqual(text_to_send, 'Данного города нет')

    def test_flight_information(self):
        dispatch_city = 'Москва'
        arrival_city = 'Питер'
        expected_flight_message = f'Рейс под номером {482} из города {dispatch_city} в город {arrival_city}' \
                                  f' вылетает {"2021-05-18"}'

        with open(file='test_dispatcher_json.json', mode='r') as file:
            flight_dispatcher = json.load(file)
        for flight in flight_dispatcher[dispatch_city][arrival_city]:
            flight_message = f'Рейс под номером {flight[1]} из города {dispatch_city} в город {arrival_city}' \
                             f' вылетает {flight[0]}'

            self.assertEqual(flight_message, expected_flight_message)
            break
