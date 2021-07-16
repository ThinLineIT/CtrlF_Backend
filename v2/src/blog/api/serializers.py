from blog.models import Post
from rest_framework.serializers import ModelSerializer


class PostSerializers(ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "author",
            "title",
            "text",
            "created_date",
            "published_date",
        ]
