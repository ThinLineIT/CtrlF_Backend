from blog.models import Post
from rest_framework.serializers import ModelSerializer, SerializerMethodField


class PostSerializers(ModelSerializer):
    author = SerializerMethodField()

    def get_author(self, post):
        return post.author.username

    class Meta:
        model = Post
        fields = [
            "author",
            "title",
            "text",
            "created_date",
            "published_date",
        ]
