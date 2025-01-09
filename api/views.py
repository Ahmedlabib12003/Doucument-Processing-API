from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound, ValidationError
from django.core.exceptions import ObjectDoesNotExist
from .serializers import (
    FileUploadSerializer,
    ImageListSerializer,
    PDFListSerializer,
    ImageDetailSerializer,
    PDFDetailSerializer,
)
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


class ImageDetailView(generics.RetrieveDestroyAPIView):
    """
    API endpoint for retrieving and deleting specific images.
    Provides detailed information about a single image and handles its deletion.
    """

    queryset = Image.objects.all()
    serializer_class = ImageDetailSerializer

    def perform_destroy(self, instance):
        """
        Custom destroy method to ensure both the database record
        and the actual file are deleted properly.
        """
        try:
            # The delete() method in our model will handle file deletion
            instance.delete()
        except Exception as e:
            raise ValidationError(f"Error deleting image: {str(e)}")

    def retrieve(self, request, *args, **kwargs):
        """
        Custom retrieve method with enhanced error handling.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            raise NotFound("Image not found")
        except Exception as e:
            return Response(
                {"error": f"Error retrieving image: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PDFDetailView(generics.RetrieveDestroyAPIView):
    """
    API endpoint for retrieving and deleting specific PDFs.
    Provides detailed information about a single PDF and handles its deletion.
    """

    queryset = PDF.objects.all()
    serializer_class = PDFDetailSerializer

    def perform_destroy(self, instance):
        """
        Custom destroy method to ensure both the database record
        and the actual file are deleted properly.
        """
        try:
            # The delete() method in our model will handle file deletion
            instance.delete()
        except Exception as e:
            raise ValidationError(f"Error deleting PDF: {str(e)}")

    def retrieve(self, request, *args, **kwargs):
        """
        Custom retrieve method with enhanced error handling.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            raise NotFound("PDF not found")
        except Exception as e:
            return Response(
                {"error": f"Error retrieving PDF: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
