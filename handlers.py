import json
import re
from datetime import datetime
from drawing.draw_ticket import AirplaneTickets

re_number = re.compile('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
re_full_name = re.compile('^[А-ЯA-Z][а-яa-zА-ЯA-Z\-]{0,}\s[А-ЯA-Z][а-яa-zА-ЯA-Z\-]{1,}'
                          '(\s[А-ЯA-Z][а-яa-zА-ЯA-Z\-]{1,})?$')


def handle_dispatch_city(text, context):
    if text:
        context['dispatch_city'] = text
        return True
    else:
        return False


def handle_arrival_city(text, context):
    if text:
        context['arrival_city'] = text
        return True
    else:
        return False


def flight_information(text, context):
    dispatch_city = context['dispatch_city']
    arrival_city = context['arrival_city']
    with open(file='dispatcher/dispatcher_json.json', mode='r') as file:
        flight_dispatcher = json.load(file)
    for flight in flight_dispatcher[dispatch_city][arrival_city]:
        flight_message = f'Рейс под номером {flight[1]} из города {dispatch_city} в город {arrival_city}' \
                         f' вылетает {flight[0]}'
        yield flight_message


def handle_date(text, context):
    try:
        datetime.strptime(text, "%d.%m.%Y")
        context['date'] = text
        return True
    except Exception:
        return False


def handle_number_ticket(text, context):
    int(text)
    with open(file='dispatcher/dispatcher_json.json', mode='r') as file:
        number = json.load(file)
    number = number[context['dispatch_city']][context['arrival_city']]
    number_list = [x[1] for x in number]
    if int(text) in number_list:
        context['number_ticket'] = text
        return True
    else:
        return False


def handle_quantity_place(text, context):
    int(text)
    number_list = [1, 2, 3, 4, 5]
    if int(text) in number_list:
        context['quantity_place'] = text
        return True
    else:
        return False


def handle_check_number(text, context):
    match = re.match(re_number, text)
    if match:
        context['phone_number'] = text
        return True
    else:
        return False


def handle_full_name(text, context):
    match = re.match(re_full_name, text)
    if match:
        context['full_name'] = text
        return True
    else:
        return False


def generate_ticket(text, context):
    ticket = AirplaneTickets(context['full_name'], context['dispatch_city'], context['arrival_city'], context['date'])
    return ticket.make_ticket()


def handle_check_user_answer(text, context):
    return text.lower() == 'да'
