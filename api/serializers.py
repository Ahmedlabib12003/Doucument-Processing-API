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
    file_type = serializers.ChoiceField(choices=['image', 'pdf'])

    def validate_file(self, value):
        """Validate the base64 encoded file."""
        try:
            # Try to decode the base64 string
            base64.b64decode(value)
            return value
        except Exception:
            raise serializers.ValidationError("Invalid base64 encoding")

    def create(self, validated_data):
        file_data = validated_data['file']
        file_type = validated_data['file_type']
        title = validated_data['title']

        # Decode base64 data
        try:
            file_content = base64.b64decode(file_data)
        except Exception as e:
            raise serializers.ValidationError(f"Error decoding base64 data: {str(e)}")

        # Generate unique filename
        filename = f"{uuid.uuid4().hex}"
        
        if file_type == 'image':
            file_path = os.path.join(settings.MEDIA_ROOT, 'images', f"{filename}.jpg")
            model_class = Image
        else:
            file_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', f"{filename}.pdf")
            model_class = PDF

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # Create model instance with file metadata
        instance = model_class(title=title, file_path=file_path)

        # Extract and save additional metadata
        try:
            if file_type == 'image':
                with PILImage.open(file_path) as img:
                    instance.width = img.width
                    instance.height = img.height
                    instance.channels = len(img.getbands())
            else:
                with open(file_path, 'rb') as f:
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