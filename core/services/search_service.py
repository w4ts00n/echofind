from core.dao.search_dao import SearchDAO
from django.urls import reverse
from pathlib import Path


class SearchService:
    @staticmethod
    def search_files(keyword: str, owner_id: str):
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"text": keyword}},
                        {"match": {"owner_id": owner_id}}
                    ]
                }
            },
            "highlight": {
                "fields": {
                    "text": {
                        "pre_tags": ["<em>"],
                        "post_tags": ["</em>"],
                    }
                }
            }
        }

        hits = SearchDAO.search_file("my_index", search_query).get("hits", {}).get("hits", [])
        results = SearchService.build_search_results(hits)

        return results

    @staticmethod
    def build_search_results(hits):
        results = {}
        for hit in hits:
            original_json_document = hit["_source"]
            matched_mp4_filename = original_json_document.get("mp4name")

            search_result_details_dict = {}
            search_result_details_dict["text"] = hit["highlight"].get("text")
            search_result_details_dict["url"] = reverse("file_api") + f"?file_name={matched_mp4_filename}"

            thumbnail_path = f"{Path(matched_mp4_filename).stem}_thumbnail.jpg"
            search_result_details_dict["thumbnail_url"] = reverse("file_api") + f"?file_name={thumbnail_path}"
            results[matched_mp4_filename] = search_result_details_dict

        return results
