from django.http import JsonResponse
from django.utils import timezone
from blog.models import Post
import json
from django.core.serializers.json import DjangoJSONEncoder


def retrieve_post_list(request):
    post_list = []
    for post in Post.objects.all():
        post_list.append(
            {
                "title": post.title,
                "text": post.text,
                "author": post.author.id,
                "created_date": post.created_date,
                "published_date": post.published_date,
            },
        )

    return JsonResponse({"posts": post_list})
