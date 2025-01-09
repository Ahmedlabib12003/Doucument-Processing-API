from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from PIL import Image as PILImage
import os
import uuid
from pdf2image import convert_from_path
from .serializers import (
    FileUploadSerializer,
    ImageListSerializer,
    PDFListSerializer,
    ImageDetailSerializer,
    PDFDetailSerializer,
    ImageRotationSerializer,
    PDFToImageSerializer,
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


class ImageRotationView(APIView):
    """
    API endpoint for rotating images.
    Creates a new image file with the rotated content and returns its details.
    """

    def post(self, request, image_id):
        try:
            # Validate input
            serializer = ImageRotationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Get the original image
            image = Image.objects.get(pk=image_id)
            angle = serializer.validated_data["angle"]

            # Open and rotate the image
            with PILImage.open(image.file_path) as img:
                # Rotate the image while maintaining full image content
                # expand=True ensures no content is lost during rotation
                rotated_img = img.rotate(
                    angle=-angle,  # Negative for clockwise rotation
                    expand=True,
                    resample=PILImage.BICUBIC,
                )

                # Generate new filename for rotated image
                filename = f"{uuid.uuid4().hex}_rotated.{img.format.lower()}"
                new_file_path = os.path.join(settings.MEDIA_ROOT, "images", filename)

                # Save the rotated image
                rotated_img.save(new_file_path, format=img.format)

            # Create new Image instance for rotated image
            rotated_image = Image.objects.create(
                title=f"{image.title}_rotated_{angle}",
                file_path=new_file_path,
                width=rotated_img.width,
                height=rotated_img.height,
                channels=len(rotated_img.getbands()),
            )

            # Return the details of the new image
            serializer = ImageDetailSerializer(rotated_image)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Image.DoesNotExist:
            return Response(
                {"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error processing image: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PDFToImageView(APIView):
    """
    API endpoint for converting PDF pages to images.
    Creates a new image file from the specified PDF page and returns its details.
    """

    def post(self, request, pdf_id):
        try:
            # Validate input
            serializer = PDFToImageSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Get the PDF document
            pdf = PDF.objects.get(pk=pdf_id)
            page_number = serializer.validated_data["page_number"]
            dpi = serializer.validated_data["dpi"]

            # Check if requested page exists
            if page_number > pdf.num_pages:
                return Response(
                    {"error": f"Page {page_number} does not exist in this PDF"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Convert PDF page to image
            images = convert_from_path(
                pdf.file_path,
                dpi=dpi,
                first_page=page_number,
                last_page=page_number,
                poppler_path="C:\Program Files (x86)\poppler\\bin",
            )
            if not images:
                raise ValidationError("Failed to convert PDF page to image")

            # Get the converted image (first and only page)
            converted_image = images[0]

            # Generate filename for the new image
            filename = f"{uuid.uuid4().hex}_page_{page_number}.jpg"
            new_file_path = os.path.join(settings.MEDIA_ROOT, "images", filename)

            # Save the converted image
            converted_image.save(new_file_path, "JPEG", quality=95)

            # Create new Image instance for the converted page
            image_instance = Image.objects.create(
                title=f"{pdf.title}_page_{page_number}",
                file_path=new_file_path,
                width=converted_image.width,
                height=converted_image.height,
                channels=len(converted_image.getbands()),
            )

            # Return the details of the new image
            serializer = ImageDetailSerializer(image_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except PDF.DoesNotExist:
            return Response(
                {"error": "PDF not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error converting PDF: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
