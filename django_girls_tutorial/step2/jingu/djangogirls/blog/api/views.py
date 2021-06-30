from django.http import JsonResponse
from django.utils import timezone

from blog.models import Post


def retrieve_post_list(request):
    """
    해당 view 함수를 구현하시오.

    응답 JSON
    {
        "posts": [
            {
                "title": "test title",
                "text": "test text",
                "author": 1,
                "created_date": "2021-01-01T00:00:00", # 시간 포맷은 다를 수 있음
                "published_date": "2021-01-01T02:00:00", # 시간 포맷은 다를 수 있음
            },
            {
                "title": "test title2",
                "text": "test text2",
                "author": 1,
                "created_date": "2021-01-02T00:00:00", # 시간 포맷은 다를 수 있음
                "published_date": "2021-01-02T03:00:00", # 시간 포맷은 다를 수 있음
            },
            {...},
            ...
        ]
    }

    or 발행된 Post가 0개 일 때,

    {
        "posts": []
    }
    """
    pass
