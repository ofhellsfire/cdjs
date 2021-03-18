"""Benchmark for `cdjs`

Benchmark compares:
    - standard `json` with `bson.json_util.default` handler
    - `orjson` with `bson.json_util.defaul` handler
    - `orjson` with `cdjs.serialize` handler
    - `orjson` with `cdjs.do_nothing` handler as a baseline
"""

from datetime import timedelta
from random import randrange, randint
import argparse
import datetime
import hashlib
import json
import time
import uuid
import sys

from bson import json_util
from bson.json_util import DEFAULT_JSON_OPTIONS
from bson.json_util import DatetimeRepresentation
from bson.objectid import ObjectId
from faker import Faker
import matplotlib.pyplot as plt
import orjson
import pytz
import seaborn as sns

from cdjs import serialize, do_nothing

fake = Faker()

DEFAULT_JSON_OPTIONS.datetime_representation = DatetimeRepresentation.ISO8601

PROGRESSIONS = [1, 100, 100000, 1000000]


def serialize_datetime_py(date):
    return json_util.default(date)


def random_datetime(start, end):
    """
    This function will return a random datetime between two datetime objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


def get_random_utc_dates(count):
    return [
        {'date': random_datetime(datetime.datetime(2000, 1, 1), datetime.datetime(2021, 1, 1))}
        for _ in range(count)
    ]


def get_random_tz_dates(count):
    return [
        {'date': random_datetime(datetime.datetime(2000, 1, 1),
                                 datetime.datetime(2021, 1, 1)).replace(
                                     tzinfo=pytz.timezone('Asia/Shanghai'))}
        for _ in range(count)
    ]


def get_random_old_dates(count):
    return [
        {'date': random_datetime(datetime.datetime(1900, 1, 1), datetime.datetime(1969, 1, 1))}
        for _ in range(count)
    ]

def get_random_json(count):
    return [
        {
            '_id': ObjectId(hashlib.md5(fake.text().encode()).hexdigest()[:24]),
            'index': randint(0, 10000),
            'guid': str(uuid.uuid4()),
            'isActive': bool(randint(0, 2)),
            'balance': f'${randint(0, 10)},{randint(100, 1000)}.{randint(10, 100)}',
            'picture': f'https://somehost.io/{randint(10, 56)}x{randint(10, 56)}',
            'age': randint(10, 99),
            'eyeColor': fake.color(),
            'name': fake.name(),
            'gender': 'male' if bool(randint(0, 2)) else 'female',
            'company': fake.company(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'address': fake.address(),
            'about': fake.text(),
            'registered': random_datetime(datetime.datetime(1971, 1, 1),
                                          datetime.datetime(2021, 1, 1)),
            'latitude': randint(10000000, 100000000) / 1000000,
            'longitude': randint(10000000, 100000000) / 1000000,
            'tags': [fake.word() for _ in range(8)],
            'friends': [{'id': randint(0, 100), 'name': fake.name()}
                        for _ in range(randint(2, 10))],
            'greeting': fake.sentence(),
            'favorite': fake.word(),
            'birthday': random_datetime(datetime.datetime(2000, 1, 1),
                                        datetime.datetime(2021, 1, 1)),
        }
        for _ in range(count)
    ]


def parse_args():
    parser = argparse.ArgumentParser(description='Benchmark')
    parser.add_argument('-s', '--scenario',
                        help='Scenario',
                        choices=['utc_dates', 'tz_dates', 'old_dates', 'json'],
                        default='utc_dates', required=True)
    return parser.parse_args()


class Benchmarks:

    @staticmethod
    def run(scenario):
        _, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize = (24, 6))
        d = { 1: ax1, 2: ax2, 3: ax3, 4: ax4 }
        x = ['std json', 'pyserial', 'rustserial', 'baseline']
        for i, prog in enumerate(PROGRESSIONS, 1):
            y = []
            dates = getattr(sys.modules[__name__], f'get_random_{scenario}')(prog)

            # std lib json with custom python serializer
            # warmup
            _ = json.dumps(
                random_datetime(datetime.datetime(2000, 1, 1), datetime.datetime(2021, 1, 1)),
                default=serialize_datetime_py
            )
            start = time.time()
            for date in dates:
                _ = json.dumps(date, default=serialize_datetime_py)
            end = time.time()
            elapsed = end - start
            y.append(elapsed)
            print(f'std lib json with custom python serializer :: took {elapsed} '
                  f'seconds to serialize {prog} datetimes')

            # orjson with custom python serializer
            # warmup
            _ = orjson.dumps(
                random_datetime(datetime.datetime(2000, 1, 1), datetime.datetime(2021, 1, 1)),
                option=orjson.OPT_PASSTHROUGH_DATETIME, default=serialize_datetime_py
            ).decode()
            start = time.time()
            for date in dates:
                _ = orjson.dumps(date,
                                 option=orjson.OPT_PASSTHROUGH_DATETIME,
                                 default=serialize_datetime_py).decode()
            end = time.time()
            elapsed = end - start
            y.append(elapsed)
            print(f'orjson with custom python serializer :: took {elapsed} '
                  f'seconds to serialize {prog} datetimes')

            # orjson with custom rust serializer
            # warmup
            _ = orjson.dumps(
                random_datetime(datetime.datetime(2000, 1, 1), datetime.datetime(2021, 1, 1)),
                option=orjson.OPT_PASSTHROUGH_DATETIME, default=serialize
            ).decode()
            start = time.time()
            for date in dates:
                _ = orjson.dumps(date,
                                 option=orjson.OPT_PASSTHROUGH_DATETIME,
                                 default=serialize).decode()
            end = time.time()
            elapsed = end - start
            y.append(elapsed)
            print(f'orjson with custom rust serializer :: took {elapsed} '
                  f'seconds to serialize {prog} datetimes')

            # orjson with empty rust serializer (baseline)
            start = time.time()
            for date in dates:
                _ = orjson.dumps(date,
                                 option=orjson.OPT_PASSTHROUGH_DATETIME,
                                 default=do_nothing).decode()
            end = time.time()
            elapsed = end - start
            y.append(elapsed)
            print(f'orjson with empty rust serializer (baseline) :: took {elapsed} '
                  f'seconds to serialize {prog} datetimes')

            print('')
            print('=' * 22)
            print('')

            sns.barplot(x, y, color='lightsteelblue', ax=d[i])
            d[i].set_xlabel(f'Count: {prog}')
            d[i].set_ylabel('Elapsed Time (s)')

        plt.show()


if __name__ == '__main__':
    args = parse_args()
    getattr(Benchmarks, 'run')(args.scenario)
