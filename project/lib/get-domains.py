from datetime import datetime
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch

client = Elasticsearch()

# Search aggregation that gets the domain_name associated with each event and
# calculates the total number of events for each domain
s = Search(using=client, index="sfn-dns-event")
s.aggs.bucket('domain-details', 'terms', field='domain_name.keyword',size=10000)
response = s.execute()

# F-strings can't do inline newlines, so we use this to fake it out
nl = '\n'

# Write this info to the file for shipping (off to Boston!!!)
fileName = datetime.strftime(datetime.now(),"%Y-%m-%d_%H-%M")
with open('udc-' + fileName + '.txt','w') as outFile:
    outFile.write(f"Total number of events: {response['hits']['total']}{nl}{nl}")
    for hit in response['aggregations']['domain-details']['buckets']:
        print(f"{hit.key}:{hit.doc_count}")
        outFile.write(f"{hit.key}:{hit.doc_count}{nl}")
