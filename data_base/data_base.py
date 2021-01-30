import peewee
from playhouse.postgres_ext import JSONField

from settings import DB_CONFIG

pg_db = peewee.PostgresqlDatabase(**DB_CONFIG)


class BaseTable(peewee.Model):
    class Meta:
        database = pg_db


class UserState(BaseTable):
    """Хранит данные о состоянии пользователя внутри сценария"""
    user_id = peewee.CharField(unique=True)
    scenario_name = peewee.CharField()
    step_name = peewee.CharField()
    context = JSONField()


class Registration(BaseTable):
    """Хранит данные которые вводит пользователь"""
    number_ticket = peewee.CharField()
    quantity_place = peewee.CharField()
    phone_number = peewee.CharField()


pg_db.create_tables([UserState])
pg_db.create_tables([Registration])
