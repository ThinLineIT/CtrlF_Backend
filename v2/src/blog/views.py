from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Post
from .serializers import PostSerializer


class PostListCreate(APIView):
    def get(self, request):
        posts = Post.objects.filter(published_date__lte=timezone.now()).order_by("published_date")
        serializer = PostSerializer(posts, many=True)
        return Response({"posts": serializer.data})

    def post(self, request):
        serializer = PostSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"post": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            for key in serializer.errors:
                if key == "author":
                    return Response({"message": "author를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
                elif key == "title":
                    return Response({"message": "title이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
                elif key == "text":
                    return Response({"message": "text가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
