import json
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_http_methods

from django.contrib.auth.models import User
from blog.models import Post, Comment


def retrieve_post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by("published_date")

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
    try:
        post = Post.objects.get(pk=id)
    except Post.DoesNotExist:
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


class CommentListCreate(View):
    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"message": "post가 없습니다."}, status=404)

        comments = Comment.objects.filter(post=post, created_date__lte=timezone.now()).order_by("created_date")
        comment_list = [{"author": comment.author, "text": comment.text} for comment in comments]

        return JsonResponse({"data": comment_list})

    def post(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"message": "post가 없습니다."}, status=404)

        body = request.POST
        if not body["author"]:
            return JsonResponse({"message": "author가 없습니다."}, status=400)
        elif not body["text"]:
            return JsonResponse({"message": "text가 없습니다."}, status=400)

        comment = Comment.objects.create(post=post, author=body["author"], text=body["text"])
        return JsonResponse({"data": {"post_id": post.id, "author": comment.author, "text": comment.text}}, status=201)
