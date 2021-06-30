from http.client import NOT_FOUND, OK

from django.http import JsonResponse
from django.utils import timezone

from blog.models import Post


def retrieve_post_list(request):
    # 해당 view 함수를 구현하시오.
    pass


def retrieve_post_detail(request, id):
    try:
        post = Post.objects.get(published_date__lte=timezone.now())
    except Post.DoesNotExist:
        return JsonResponse(status=NOT_FOUND, data={"message": "Post를 찾을 수 없습니다"})
    else:
        return JsonResponse(
            status=OK,
            data={
                "post": {
                    "author": post.author.id,
                    "title": post.title,
                    "text": post.text,
                    "created_date": post.created_date,
                    "published_data": post.published_date,
                }
            },
        )
