# models.py
from django.db import models
import os

class BaseDocument(models.Model):
    """
    Abstract base model for both Image and PDF documents.
    Contains common fields and functionality.
    """
    title = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        # Delete the actual file when model instance is deleted
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        super().delete(*args, **kwargs)

class Image(BaseDocument):
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    channels = models.IntegerField(null=True)  # Number of color channels

    def __str__(self):
        return f"Image: {self.title}"

class PDF(BaseDocument):
    num_pages = models.IntegerField(null=True)
    page_width = models.FloatField(null=True)
    page_height = models.FloatField(null=True)

    def __str__(self):
        return f"PDF: {self.title}"