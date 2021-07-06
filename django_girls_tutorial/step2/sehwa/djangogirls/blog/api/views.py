import json
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from django.contrib.auth.models import User
from blog.models import Post


def retrieve_post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by(
        "published_date"
    )

    post_list = [
        {
            "title": post.title,
            "text": post.text,
            "author": post.author.id,
            "created_date": post.created_date,
            "published_date": post.published_date,
        }
        for post in posts
    ]
    return JsonResponse({"posts": post_list})


def retrieve_post_detail(request, id):
    """
    해당 view 함수를 구현하시오.

    Case 1: 성공하는 경우,

    응답 JSON
    {
        "post": {
            "author": 1,
            "title": "test title",
            "text": "test text",
            "created_date": "2021-01-01T00:00:00" # 포맷은 다를 수 있음
            "published_date": "2021-01-02T01:00:00" # 포맷은 다를 수 있음
        }
    }
    상태코드 200

    Case 2: 실패하는 경우, - 검색하려는 Post가 존재하지 않음

    응답 JSON
    {
        "message": "Post를 찾을 수 없습니다"
    }
    상태코드 404
    """


@require_http_methods(["POST"])
def create_post(request):
    body = request.POST
    title = body["title"]
    text = body["text"]

    try:
        user = User.objects.get(pk=body.get("author"))
    except User.DoesNotExist:
        return JsonResponse({"message": "author를 찾을 수 없습니다."}, status=404)

    else:
        Post.objects.create(author=user, title=body.get("title"), text=body.get("text"))
        return JsonResponse(
            {"post": {"author": user.id, "title": title, "text": text}}, status=201
        )


@require_http_methods(["PUT"])
def update_post_with_put(request, id):
    body = json.loads(request.body.decode("utf-8"))

    try:
        user = User.objects.get(pk=body["author"])
        post = Post.objects.get(pk=id)
    except User.DoesNotExist:
        return JsonResponse({"message": "author를 찾을 수 없습니다."}, status=404)
    except Post.DoesNotExist:
        return JsonResponse({"message": "post를 찾을 수 없습니다."}, status=404)

    else:
        post.title = body["title"]
        post.text = body["text"]

        post.save()
        return JsonResponse(
            {"post": {"author": user.id, "title": post.title, "text": post.text}},
            status=200,
        )
