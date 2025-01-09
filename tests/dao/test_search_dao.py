from core.dao.search_dao import SearchDAO


def test_search_dao(mocker):
    mock_es_client = mocker.patch('core.dao.search_dao.es_client')
    keyword = "keyword"
    owner_id = "user123"
    index = "my_index"

    search_query = {
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"text": keyword}},
                    {"match": {"owner_id": owner_id}}
                ]
            }
        }
    }

    SearchDAO.search_file(index, search_query)

    mock_es_client.search.assert_called_once_with(index="my_index", body=search_query)
