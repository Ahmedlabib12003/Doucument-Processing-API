from django.urls import path
from .views import FileUploadView, ImageListView, PDFListView

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path("images/", ImageListView.as_view(), name="image-list"),
    path("pdfs/", PDFListView.as_view(), name="pdf-list"),
]
