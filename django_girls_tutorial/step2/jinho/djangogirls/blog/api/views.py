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
