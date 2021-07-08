from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from blog.models import Post


def retrieve_post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by(
        "published_date"
    )

    result = [
        {
            "title": post.title,
            "text": post.text,
            "author": post.author.id,
            "created_date": post.created_date,
            "published_date": post.published_date,
        }
        for post in posts
    ]

    return JsonResponse({"posts": result})


def retrieve_post_detail(request, id):
    try:
        post = Post.objects.get(id=id)
    except:
        return JsonResponse({"message": "Post를 찾을 수 없습니다"}, status=404)
    else:
        return JsonResponse(
            {
                "post": {
                    "author": post.author.id,
                    "title": post.title,
                    "text": post.text,
                    "created_date": post.created_date,
                    "published_date": post.published_date,
                }
            },
            status=200,
        )
