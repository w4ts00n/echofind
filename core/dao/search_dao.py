from .es_client import es_client


class SearchDAO:
    @staticmethod
    def search_file(index: str, search_query: dict):
        return es_client.search(index=index, body=search_query)
