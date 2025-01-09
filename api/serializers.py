from rest_framework import serializers
import base64
import uuid
import os
from PIL import Image as PILImage
from pypdf import PdfReader
from django.conf import settings
from .models import Image, PDF
import uuid


class FileUploadSerializer(serializers.Serializer):
    """
    Serializer for handling file uploads in base64 format.
    """

    file = serializers.CharField()  # Base64 encoded file
    title = serializers.CharField()
    file_type = serializers.ChoiceField(choices=["image", "pdf"])

    def validate_file(self, value):
        """Validate the base64 encoded file."""
        try:
            # Try to decode the base64 string
            base64.b64decode(value)
            return value
        except Exception:
            raise serializers.ValidationError("Invalid base64 encoding")

    def create(self, validated_data):
        file_data = validated_data["file"]
        file_type = validated_data["file_type"]
        title = validated_data["title"]

        # Decode base64 data
        try:
            file_content = base64.b64decode(file_data)
        except Exception as e:
            raise serializers.ValidationError(f"Error decoding base64 data: {str(e)}")

        # Generate unique filename
        filename = f"{uuid.uuid4().hex}"

        if file_type == "image":
            file_path = os.path.join(settings.MEDIA_ROOT, "images", f"{filename}.jpg")
            model_class = Image
        else:
            file_path = os.path.join(settings.MEDIA_ROOT, "pdfs", f"{filename}.pdf")
            model_class = PDF

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Create model instance with file metadata
        instance = model_class(title=title, file_path=file_path)

        # Extract and save additional metadata
        try:
            if file_type == "image":
                with PILImage.open(file_path) as img:
                    instance.width = img.width
                    instance.height = img.height
                    instance.channels = len(img.getbands())
            else:
                with open(file_path, "rb") as f:
                    pdf = PdfReader(f)
                    instance.num_pages = len(pdf.pages)
                    # Get dimensions of first page
                    page = pdf.pages[0]
                    instance.page_width = float(page.mediabox.width)
                    instance.page_height = float(page.mediabox.height)
        except Exception as e:
            # If metadata extraction fails, delete the file and raise error
            os.remove(file_path)
            raise serializers.ValidationError(f"Error processing file: {str(e)}")

        instance.save()
        return instance


class ImageListSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = [
            "id",
            "title",
            "file_url",
            "width",
            "height",
            "channels",
            "uploaded_at",
        ]

    def get_file_url(self, obj):
        """
        Convert the file path to a URL relative to MEDIA_URL.
        This makes it easier for clients to construct the full URL to the image.
        """
        if obj.file_path:
            # Remove MEDIA_ROOT prefix to get relative path
            relative_path = os.path.relpath(obj.file_path, settings.MEDIA_ROOT)
            return os.path.join(settings.MEDIA_URL, relative_path)
        return None


class PDFListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing PDF documents with their metadata.
    Similar to ImageListSerializer, we include a relative URL for file access.
    """

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PDF
        fields = [
            "id",
            "title",
            "file_url",
            "num_pages",
            "page_width",
            "page_height",
            "uploaded_at",
        ]

    def get_file_url(self, obj):
        """
        Convert the file path to a URL relative to MEDIA_URL.
        """
        if obj.file_path:
            relative_path = os.path.relpath(obj.file_path, settings.MEDIA_ROOT)
            return os.path.join(settings.MEDIA_URL, relative_path)
        return None


class ImageDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed image information.
    Includes all metadata and file information for a single image.
    """

    file_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = [
            "id",
            "title",
            "file_url",
            "width",
            "height",
            "channels",
            "uploaded_at",
            "file_size",
            "mime_type",
        ]

    def get_file_url(self, obj):
        if obj.file_path:
            relative_path = os.path.relpath(obj.file_path, settings.MEDIA_ROOT)
            return os.path.join(settings.MEDIA_URL, relative_path)
        return None

    def get_file_size(self, obj):
        """Returns the file size in bytes"""
        try:
            return os.path.getsize(obj.file_path)
        except (OSError, FileNotFoundError):
            return None

    def get_mime_type(self, obj):
        """Determines the MIME type of the image"""
        try:
            with PILImage.open(obj.file_path) as img:
                return f"image/{img.format.lower()}"
        except Exception:
            return "image/unknown"


class PDFDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed PDF information.
    Includes comprehensive metadata about the PDF document.
    """

    file_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    creation_date = serializers.SerializerMethodField()

    class Meta:
        model = PDF
        fields = [
            "id",
            "title",
            "file_url",
            "num_pages",
            "page_width",
            "page_height",
            "uploaded_at",
            "file_size",
            "author",
            "creation_date",
        ]

    def get_file_url(self, obj):
        if obj.file_path:
            relative_path = os.path.relpath(obj.file_path, settings.MEDIA_ROOT)
            return os.path.join(settings.MEDIA_URL, relative_path)
        return None

    def get_file_size(self, obj):
        """Returns the file size in bytes"""
        try:
            return os.path.getsize(obj.file_path)
        except (OSError, FileNotFoundError):
            return None

    def get_author(self, obj):
        """Extracts author information from PDF metadata"""
        try:
            with open(obj.file_path, "rb") as f:
                pdf = PdfReader(f)
                return pdf.metadata.get("/Author", None)
        except Exception:
            return None

    def get_creation_date(self, obj):
        """Extracts creation date from PDF metadata"""
        try:
            with open(obj.file_path, "rb") as f:
                pdf = PdfReader(f)
                return pdf.metadata.get("/CreationDate", None)
        except Exception:
            return None
