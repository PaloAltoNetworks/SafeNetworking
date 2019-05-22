from elasticsearch import Elasticsearch, helpers
import sys, json

es = Elasticsearch()

def load_json(filename):
    if filename.endswith('.json'):
        with open(filename,'r') as open_file:
            yield json.load(open_file)

helpers.bulk(es, load_json(sys.argv[1]), index='sfn-tag-details')