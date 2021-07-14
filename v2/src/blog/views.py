from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Post
from .serializers import PostSerializer


class PostListCreate(APIView):
    def get(self, request):
        posts = Post.objects.filter(published_date__lte=timezone.now()).order_by("published_date")
        serializer = PostSerializer(posts, many=True)
        return Response({"posts": serializer.data})
