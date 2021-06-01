import pandas as pd
import datetime

from mongoengine.connection import connect
from mongoengine.document import Document
from mongoengine.fields import StringField, DateTimeField
from elasticsearch import Elasticsearch
from elasticsearch import helpers

from utils import timer

es = Elasticsearch([{'host': '10.10.10.10', 'port': 9200}])

connect('check_black_kw',
        alias='blackkw',
        host='10.10.10.10',
        port=7238,
        username='root',
        password='example',
        authentication_source='admin')


class CommonRecord(Document):
    # Basic Info
    key_id = StringField(max_length=250, required=True, primary_key=True)
    start_time = DateTimeField(required=True)
    duration = StringField(max_length=50, required=True)
    caller_number = StringField(max_length=50, required=True)
    called_number = StringField(max_length=50, required=True)
    call_type = StringField(max_length=50, required=True)
    account_name = StringField(max_length=50)
    app_name = StringField(max_length=50)

    # Processed Info
    asr_raw = StringField()
    content_clean = StringField()
    content_cut = StringField()
    common_kw = StringField()
    risk_kw = StringField()

    meta = {'db_alias': 'blackkw'}


def cust_cdr(start_time, end_time):
    pipeline_cdr = [
        {'$match': {'$and': [
            {'start_time': {'$gte': pd.to_datetime(start_time + " 00:00:00"),
                            '$lte': pd.to_datetime(end_time + " 23:59:59")}
             },
        ]}},
    ]
    results = CommonRecord._get_collection().aggregate(pipeline_cdr)
    df_cdr = pd.DataFrame(results)
    df_cdr.reset_index(drop=True, inplace=True)
    return df_cdr


def gendata(df):
    num_rows = len(df.index.values)
    for i in range(num_rows):
        df_i = df.loc[i, :]
        yield {
            "_index": "s2",
            "_id": df_i._id,
            # Basic Info
            "start_time": df_i.start_time,
            "duration": df_i.duration,
            "caller_number": df_i.caller_number,
            "called_number": df_i.called_number,
            "call_type": df_i.call_type,
            "account_name": df_i.account_name,

            # Processed Info
            "asr_raw": df_i.asr_raw,
            "content_clean": df_i.content_clean,
            "content_cut": df_i.content_cut,
            "common_kw": df_i.common_kw,
            "risk_kw": df_i.risk_kw,
            "update_time": datetime.datetime.now(),
        }


@timer
def write_to_es(df):
    helpers.bulk(es, gendata(df))


if __name__ == "__main__":

    start_day = datetime.datetime(2021, 4, 26).date()
    start_day = start_day.strftime("%Y-%m-%d")
    end_day = datetime.datetime(2021, 4, 30).date()
    end_day = end_day.strftime("%Y-%m-%d")
    df = cust_cdr(start_day, end_day)
    num_rows = len(df.index.values)
    print(f"Load {num_rows} rows.")

    write_to_es(df)
