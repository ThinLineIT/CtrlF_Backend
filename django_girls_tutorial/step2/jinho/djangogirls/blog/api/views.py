import json
from http.client import NOT_FOUND, OK

from django.contrib.auth.models import User
from django.http import JsonResponse, QueryDict
from django.utils import timezone
from django.views.decorators.http import require_http_methods

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
    data = request.POST
    try:
        author = User.objects.get(id=data["author"])
    except User.DoesNotExist:
        return JsonResponse(status=404, data={"message": "author를 찾을 수 없습니다."})
    post = Post.objects.create(author=author, title=data["title"], text=data["text"])
    return JsonResponse(status=201, data={"post": {"title": post.title, "text": post.text, "author": author.username}})


@require_http_methods(["PUT"])
def update_post_with_put(request, id):
    request_body = json.loads(request.body)
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return JsonResponse(status=404, data={"message": "post를 찾을 수 없습니다."})
    try:
        author = User.objects.get(id=request_body["author"])
    except User.DoesNotExist:
        return JsonResponse(status=404, data={"message": "author를 찾을 수 없습니다."})

    post.author = author
    post.title = request_body["title"]
    post.text = request_body["text"]
    post.save()

    return JsonResponse(status=200, data={"post": {"title": post.title, "text": post.text, "author": author.username}})