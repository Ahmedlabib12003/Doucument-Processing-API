# Document Processing API

A Django REST API for processing images and PDF files. This API allows users to upload, manage, and transform documents through various endpoints.

## Features

- Upload images and PDFs (base64 encoded)
- List all uploaded documents
- View detailed information about specific documents
- Rotate images to specified angles
- Convert PDF pages to images
- Delete documents

## Prerequisites

- Docker
- Docker Compose

## Installation & Running

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <repository-name>
   ```

2. Build the Docker image:
   ```bash
   docker-compose build
   ```

3. Start the container:
   ```bash
   docker-compose up
   ```

The API will be available at http://localhost:8000

## API Endpoints

### Document Upload
- `POST /api/upload/`
  - Accepts base64 encoded files
  - Required fields:
    - `file`: Base64 encoded file content
    - `title`: Document title
    - `file_type`: Either 'image' or 'pdf'

### Image Operations
- `GET /api/images/` - List all images
- `GET /api/images/{id}/` - Get image details
- `DELETE /api/images/{id}/` - Delete an image
- `POST /api/rotate/{id}/` - Rotate an image
  - Required field: `angle` (degrees, between -360 and 360)

### PDF Operations
- `GET /api/pdfs/` - List all PDFs
- `GET /api/pdfs/{id}/` - Get PDF details
- `DELETE /api/pdfs/{id}/` - Delete a PDF
- `POST /api/convert-pdf-to-image/{id}/` - Convert PDF page to image
  - Optional fields:
    - `page_number`: Page to convert (default: 1)
    - `dpi`: Resolution of output image (default: 200)

## Example Usage

### Uploading an Image
```bash
curl -X POST http://localhost:8000/api/upload/ \
  -H "Content-Type: application/json" \
  -d '{
    "file": "base64_encoded_image_content",
    "title": "Example Image",
    "file_type": "image"
  }'
```

### Rotating an Image
```bash
curl -X POST http://localhost:8000/api/rotate/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "angle": 90
  }'
```

### Converting PDF to Image
```bash
curl -X POST http://localhost:8000/api/convert-pdf-to-image/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "page_number": 1,
    "dpi": 200
  }'
```


## Technologies Used

- Django
- Django REST Framework
- Pillow (for image processing)
- pdf2image (for PDF conversion)
- PyPDF (for PDF metadata)
- Docker
