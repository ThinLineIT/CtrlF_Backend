from django.http import JsonResponse

from blog.models import Post


def retrieve_post_list(request):
    posts_list = list(Post.objects.filter(published_date__isnull=False).values())
    posts_dict = {"posts": posts_list}
    return JsonResponse(posts_dict)