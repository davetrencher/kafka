#http://carrefax.com/new-blog/2018/3/12/load-json-files-into-elasticsearch
import requests, json, os
from elasticsearch import Elasticsearch

class ElasticSearchHelper(object):

    INDEX_NAME_FLIGHT_DATA = 'flight_data'

    es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])
    # delete index if exists
    if es.indices.exists(INDEX_NAME_FLIGHT_DATA):
        es.indices.delete(index=INDEX_NAME_FLIGHT_DATA)

    # index settings
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "_doc": {
                "properties": {
                    "name": { "type": "text" },
                    "active_stage": { "type": "short" },
                    "decouple_stage": { "type": "short" },
                    "situation": { "type": "text" },
                    "wet_mass": { "type": "float" },
                    "weight": { "type": "float" },
                    "avail_thrust": { "type": "float" },
                    "max_thrust": { "type": "float" },
                    "thrust": { "type": "float" },
                    "twr": { "type": "float" },
                    "liquid_fuel_level": { "type": "float" },
                    "solid_fuel_level": { "type": "float" },
                    "mission_elapsed_time": { "type": "double" },
                    "timestamp": {
                        "type": "date",
                        "format": "epoch_millis"
                    }
                }
            }
        }
    }

    # fix timestamp format
    # https://stackoverflow.com/questions/29371953/kibana-doesnt-show-any-results-in-discover-tab

    es.indices.create(index=INDEX_NAME_FLIGHT_DATA, ignore=400, body=settings)

    @staticmethod
    def log(vessel_name, json_log):
        ElasticSearchHelper.es.index(index='flight_data', ignore=400, body=json.loads(json_log))