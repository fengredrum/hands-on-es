from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q, Search
import pandas as pd

es = Elasticsearch([{'host': '10.10.10.10', 'port': 9200}])

delete_docs = False

query = Q('range', update_time={'gte': "2021-06-01T01:31:00"}) | Q('range', title={'lte': 10})
s = Search(using=es, index='s2').query(query)
if delete_docs:
    s.delete()
documents = [hit.to_dict() for hit in s.scan()]
df = pd.DataFrame.from_records(documents)
num_rows = len(df.index.values)
print(df)
print(f'nomber of rows: {num_rows}')
