from core.services.search_service import SearchService


def test_build_search_results(mocker):
    hits = [
        {
            "_source": {
                "mp4name": "video1.mp4",
                "text": "Test transcription",
                "owner_id": "user1"
            },
            "highlight": {
                "text": "Test transcription",
            }
        },
        {
            "_source": {
                "mp4name": "video2.mp4",
                "text": "Test transcription2",
                "owner_id": "user2"
            },
            "highlight": {
                "text": "Test transcription2",
            }
        }
    ]

    mocker.patch("core.services.search_service.reverse", return_value='/file/')

    results = SearchService.build_search_results(hits)

    expected_results = {
        'video1.mp4': {
            'text': 'Test transcription',
            'url': '/file/?file_name=video1.mp4',
            'thumbnail_url': '/file/?file_name=video1_thumbnail.jpg'
        },
        'video2.mp4': {
            'text': 'Test transcription2',
            'url': '/file/?file_name=video2.mp4',
            'thumbnail_url': '/file/?file_name=video2_thumbnail.jpg'
        }
    }

    assert results == expected_results


def test_search_files(mocker):
    keyword = "example"
    owner_id = "user1"

    mock_hits = {
            "_source": {
                "mp4name": "video1.mp4",
                "text": "Test example transcription",
                "owner_id": owner_id
            },
            "highlight": {
                "text": "Test <em>example</em> transcription",
            }
        }

    mocker.patch("core.services.search_service.reverse", return_value='/file/')
    mocker.patch("core.dao.search_dao.SearchDAO.search_file", return_value={"hits": {"hits": [mock_hits]}})

    expected_results = {
        'video1.mp4': {
            'text': 'Test <em>example</em> transcription',
            'url': '/file/?file_name=video1.mp4',
            'thumbnail_url': '/file/?file_name=video1_thumbnail.jpg'
        }
    }

    results = SearchService.search_files(keyword, owner_id)

    assert results == expected_results
    