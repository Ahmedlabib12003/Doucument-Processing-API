from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import FileUploadSerializer

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

