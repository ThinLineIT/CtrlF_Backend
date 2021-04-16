from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView


@swagger_auto_schema(method='get')
class CategoryListView(APIView):
    def get(self, request):
        return Response({"Hello": "Category"})
