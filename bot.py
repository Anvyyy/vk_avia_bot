import random

import vk_api
import vk_api.bot_longpoll
import logging
import requests

import handlers
from data_base.data_base import UserState, Registration
from settings import TOKEN, GROUP_ID, SCENARIOS, INTENTS, DEFAULT_ANSWER, CITY_LIST, HELP
from dispatcher.dispatcher import json_dispatcher

group_id = GROUP_ID
TOKEN = TOKEN
intents = INTENTS
log = logging.getLogger('exeption.log')
json_dispatcher()


def create_log():
    file_handler = logging.FileHandler('bot_file_log', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)
    log.setLevel(logging.DEBUG)


class Bot:
    """
    Поиск авиабилетов через vk
    """

    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = vk_api.bot_longpoll.VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        for event in self.long_poller.listen():
            print('Получено событие')
            try:
                self.on_event(event=event)
            except Exception as ex:
                print(f'Ошибка {ex}')

    def on_event(self, event):
        """Получаем событие"""
        if event.type != vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            log.info('Мы пока не умеем обрабатывать собитя данного типа %S', event.type)
            return

        user_id = event.message.peer_id
        text = event.message.text
        try:
            state = UserState.get(UserState.user_id == user_id)
        except:
            print('Это новый пользователь')
            state = None

        if state:
            self.continue_scenario(user_id, text, state)
        # if text == '/ticket':
        #     state.delete_instance()
        elif text == '/help':
            self.send_text(HELP, user_id)
        else:
            for intent in intents:
                if text == intent['tokens']:
                    if intent['answer']:
                        self.send_text(intent['answer'], user_id)
                    else:
                        self.start_scenario(scenario_name=[intent['scenario']], user_id=user_id, text=text)
                    break
            else:
                self.send_text(DEFAULT_ANSWER, user_id)

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id)

    def send_image(self, image, user_id):
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(url=upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachments = f'photo{owner_id}_{media_id}'
        self.api.messages.send(
            attachment=attachments,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id)

    def send_step(self, step, user_id, text, context):
        if 'text' in step:
            self.send_text(step['text'].format(**context), user_id)
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(text, context)
            self.send_image(image=image, user_id=user_id)

    def start_scenario(self, user_id, scenario_name, text):
        """Начало сценария"""
        scenario = SCENARIOS[scenario_name[0]]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        bd = UserState.create(user_id=user_id, scenario_name=scenario_name[0], step_name=first_step, context={})
        bd.save()
        self.send_step(step, user_id, text, context={})

    def continue_scenario(self, user_id, text, state):
        """Продолжение сценария"""
        if text == '/help':
            text_to_send = HELP
            return text_to_send
        steps = SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(handlers, step['handler'])
        # print(f'{state.context}')
        if handler(text=text, context=state.context):
            next_step = steps[step['next_step']]
            # print(f'{state.context}')
            if next_step['next_step']:
                state.step_name = step['next_step']
                state.save()
            else:
                reg_db = Registration.create(number_ticket=state.context["number_ticket"],
                                             quantity_place=state.context["quantity_place"],
                                             phone_number=state.context["phone_number"])
                reg_db.save()
                state.delete_instance()
            if next_step['next_step'] == 'step4':
                if state.context['dispatch_city'] not in CITY_LIST:
                    text_to_send = f'Нет авиа сообщения из этого города {state.context["dispatch_city"]}'
                    self.send_text(text_to_send, user_id)
                    state.context['dispatch_city'] = None
                    state.step_name = 'step1'
                elif state.context['arrival_city'] not in CITY_LIST:
                    text_to_send = f'Нет авиа сообщения в этот город {state.context["arrival_city"]}'
                    self.send_text(text_to_send, user_id)
                    state.context['arrival_city'] = None
                    state.step_name = 'step2'
                state.save()
            self.send_step(next_step, user_id, text, state.context)
            if next_step['next_step'] == 'step5':
                for send_messages in handlers.flight_information(text=text, context=state.context):
                    self.send_text(send_messages, user_id)
        else:
            text_to_send = step['fail_text'].format(**state.context)
            self.send_text(text_to_send, user_id)


if __name__ == '__main__':
    bot = Bot(group_id=group_id, token=TOKEN)
    bot.run()
