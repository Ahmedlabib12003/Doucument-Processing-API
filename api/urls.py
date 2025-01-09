from django.urls import path
from .views import (
    FileUploadView,
    ImageListView,
    PDFListView,
    ImageDetailView,
    PDFDetailView,
    ImageRotationView,
    PDFToImageView,
)

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path("images/", ImageListView.as_view(), name="image-list"),
    path("pdfs/", PDFListView.as_view(), name="pdf-list"),
    path("images/<int:pk>/", ImageDetailView.as_view(), name="image-detail"),
    path("pdfs/<int:pk>/", PDFDetailView.as_view(), name="pdf-detail"),
    path("rotate/<int:image_id>/", ImageRotationView.as_view(), name="image-rotate"),
    path(
        "convert-pdf-to-image/<int:pdf_id>/",
        PDFToImageView.as_view(),
        name="pdf-to-image",
    ),
]
