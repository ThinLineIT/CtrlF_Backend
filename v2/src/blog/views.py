from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Post
from .serializers import PostSerializer


class PostDetailUpdateDelete(APIView):
    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"message": "Post를 찾을 수 없습니다"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"post": PostSerializer(post).data})
