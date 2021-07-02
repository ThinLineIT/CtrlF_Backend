from http.client import NOT_FOUND, OK

from django.http import JsonResponse
from django.utils import timezone
from blog.models import Post


def retrieve_post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by("published_date")

    serialized_data = [
        {
            "title": post.title,
            "text": post.text,
            "author": post.author_id,
            "created_date": post.created_date,
            "published_date": post.published_date,
        }
        for post in posts
    ]

    return JsonResponse({"posts": serialized_data})


def retrieve_post_detail(request, id):
    try:
        detail_post = Post.objects.get(id=id)
        return JsonResponse({"post": {
            "author": detail_post.author_id,
            "title": detail_post.title,
            "text": detail_post.text,
            "created_date": detail_post.created_date,
            "published_date": detail_post.published_date,
        }}, status=OK)
    except Post.DoesNotExist:
        return JsonResponse({"message": "Post를 찾을 수 없습니다"}, status=NOT_FOUND)
