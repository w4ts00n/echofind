from elasticsearch import Elasticsearch
from core.secrets import es_hosts, es_api_key


class EsClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = Elasticsearch(
                hosts=es_hosts,
                api_key=es_api_key
            )
            return cls._instance


es_client = EsClient()
