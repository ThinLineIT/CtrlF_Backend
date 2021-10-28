from django.urls import path

from .views import PageCreateView, PageDetailUpdateDeleteView

app_name = "pages"

urlpatterns = [
    path("", PageCreateView.as_view(), name="page_create"),
    path("<int:page_id>/", PageDetailUpdateDeleteView.as_view(), name="page_detail"),
]
