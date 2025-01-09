from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .serializers import FileUploadSerializer, ImageListSerializer, PDFListSerializer
from .models import Image, PDF


class FileUploadView(APIView):
    """
    API endpoint for handling file uploads.
    """

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                instance = serializer.save()
                return Response(
                    {
                        "message": "File uploaded successfully",
                        "id": instance.id,
                        "title": instance.title,
                        "file_path": instance.file_path,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageListView(generics.ListAPIView):
    """
    API endpoint that lists all uploaded images.
    Uses Django REST Framework's generic views to handle GET requests automatically.
    Includes pagination for better performance with large datasets.
    """

    queryset = Image.objects.all().order_by("-uploaded_at")
    serializer_class = ImageListSerializer
    pagination_class = PageNumberPagination


class PDFListView(generics.ListAPIView):
    """
    API endpoint that lists all uploaded PDFs.
    Similar to ImageListView, handles GET requests and includes pagination.
    """

    queryset = PDF.objects.all().order_by("-uploaded_at")
    serializer_class = PDFListSerializer
    pagination_class = PageNumberPagination
