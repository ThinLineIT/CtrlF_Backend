from blog.models import Post
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from .serializers import PostSerializers


class PostRetrieveListView(APIView):
    def get(self, request):
        post = Post.objects.filter(published_date__lte=timezone.now()).order_by("published_date")
        serialize = PostSerializers(post, many=True)
        return Response({"posts": serialize.data}, status=HTTP_200_OK)


class PostRetrieveDetailView(APIView):
    def get(self, request, id):
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            return Response({"message": "post를 찾을 수 없습니다."}, status=HTTP_404_NOT_FOUND)
        else:
            serialize = PostSerializers(post)
            return Response({"post": serialize.data}, status=HTTP_200_OK)
