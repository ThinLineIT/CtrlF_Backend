from django.http import JsonResponse
from django.utils import timezone

from blog.models import Post


def retrieve_post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now())

    result = {}
    result["posts"] = []

    for post in posts:
        temp_post = {}
        temp_post["title"] = post.title
        temp_post["text"] = post.text
        temp_post["author"] = post.author.id
        temp_post["created_date"] = post.created_date
        temp_post["published_date"] = post.published_date
        result["posts"].append(temp_post)

    return JsonResponse(result)
