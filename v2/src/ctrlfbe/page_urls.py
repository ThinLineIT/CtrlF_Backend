from django.urls import path

from .views import PageDetailUpdateDeleteView

app_name = "pages"

urlpatterns = [
    path("<int:page_id>", PageDetailUpdateDeleteView.as_view(), name="page_detail"),
]
