from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from blog.models import Post
from django.contrib.auth.models import User
from blog.form import PostForm

from http.client import NOT_FOUND, OK, CREATED
import json


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

    return JsonResponse({"posts": result}, status=OK)


def retrieve_post_detail(request, id):
    try:
        post = Post.objects.get(id=id)
    except:
        return JsonResponse({"message": "Post를 찾을 수 없습니다"}, status=NOT_FOUND)

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
        status=OK,
    )


@require_http_methods(["POST"])
def create_post(request):
    try:
        user = User.objects.get(id=request.POST["author"])
    except:
        return JsonResponse(
            {
                "message": "author를 찾을 수 없습니다.",
            },
            status=NOT_FOUND,
        )

    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = user
        post.save()
        return JsonResponse(
            {"post": {"title": post.title, "text": post.text}}, status=CREATED
        )


@require_http_methods(["PUT"])
def update_post_with_put(request, id):
    body = json.loads(request.body)

    try:
        user = User.objects.get(id=body["author"])
    except:
        return JsonResponse(
            {
                "message": "author를 찾을 수 없습니다.",
            },
            status=NOT_FOUND,
        )

    try:
        post = Post.objects.get(id=id)
    except:
        return JsonResponse(
            {
                "message": "post를 찾을 수 없습니다.",
            },
            status=NOT_FOUND,
        )

    form = PostForm(body, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = user
        post.save()
        return JsonResponse(
            {"post": {"title": post.title, "text": post.text}}, status=OK
        )
