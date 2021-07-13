import json
from http import HTTPStatus

from django.contrib.auth.models import User
from django.http import JsonResponse, QueryDict
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from blog.form import CommentForm
from blog.models import Post, Comment


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
    """
    해당 view 함수를 구현하시오.

    Case 1: 성공하는 경우,
    상태코드 200

    Case 2: 실패하는 경우, - author가 존재하지 않음
    상태코드 404

    자세한 조건은 테스트를 확인해보고 파악하자

    FYI, request.POST 활용
    """


@require_http_methods(["PUT"])
def update_post_with_put(request, id):
    """
    해당 view 함수를 구현하시오.

    Case 1: 성공하는 경우,
    상태코드 200

    Case 2: 실패하는 경우, - author가 존재하지 않음
    Case 3: 실패하는 경우, - post가 존재하지 않음
    상태코드 404

    자세한 조건은 테스트를 확인해보고 파악하자

    FYI, request.body 활용
    """


@require_http_methods(["POST"])
def create_comment_to_post(request):
    body = request.POST
    comment_form = CommentForm(body)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.author = body["author"]
        comment.post = Post.objects.get(id=body["post_id"])
        comment.text = body["text"]
        comment.save()
        return JsonResponse({
            "comment": {
                "id": comment.id,
                "author": comment.author,
                "post_id": comment.post.id,
                "text": comment.text,
            }
        }, status=HTTPStatus.CREATED)
    return JsonResponse({"message": "form is invalid"}, status=HTTPStatus.BAD_REQUEST)
