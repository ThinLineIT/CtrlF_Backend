from blog.models import Post
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PostSerializers


class PostRetrieveListView(APIView):
    def get(self, request):
        post = Post.objects.filter(published_date__lte=timezone.now()).order_by("published_date")
        serialize = PostSerializers(post, many=True)
        return Response({"posts": serialize.data})
