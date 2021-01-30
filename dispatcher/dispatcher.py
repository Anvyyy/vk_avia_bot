import random
import json
from datetime import datetime, date
from settings import CITY_LIST


def dispatcher(city_list=CITY_LIST):
    out_dict = {}
    for i in city_list:
        out_dict[i] = {}
        x = [x for x in city_list if x != i]
        for d in x:
            out_dict[i][d] = []
            for _ in range(5):
                start_date = datetime.now().date().toordinal()
                end_date = date(day=31, month=5, year=2021).toordinal()
                random_day = date.fromordinal(random.randint(start_date, end_date))
                out_dict[i][d].append([str(random_day), random.randint(0, 1000)])
    return out_dict


def json_dispatcher(out_dict=None):
    if out_dict is None:
        out_dict = dispatcher()
    with open(file='dispatcher_json.json', mode="w", encoding="utf-8") as out_file:
        json.dump(out_dict, out_file, indent=1)



