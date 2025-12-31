# ChromaDB API Postman Collection

A comprehensive Postman collection for interacting with the ChromaDB vector database through the AI Tutor backend API.

## 📋 Overview

This collection provides endpoints for:
- **Database Health & Status** - Check database health and get statistics
- **Document Upload** - Upload files, text, or structured content to ChromaDB
- **Document Retrieval** - List documents and search using natural language queries
- **Document Management** - Delete documents from the database
- **Database Management** - Backup and reset operations

## 🚀 Quick Start

### 1. Import the Collection

1. Open Postman
2. Click **Import** button
3. Select `ChromaDB-API-Collection.json`
4. The collection will appear in your Postman workspace

### 2. Set Up Environment Variables

The collection uses the following variables:
- `base_url` - Base URL for the API (default: `http://localhost:8000`)
- `document_id` - Document ID or filename for operations (default: `sample_document.pdf`)

You can either:
- Use the existing `Ai-Tutor-Postman-Environment.json` environment file
- Create a new environment and set the variables manually
- Set variables directly in the collection

### 3. Start the Backend Server

Make sure your backend server is running:
```bash
cd backend_python
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📚 Collection Structure

### 1. Database Health & Status

#### Get Database Health Check
- **Endpoint:** `GET /api/health`
- **Description:** Check the health status of ChromaDB and related services
- **Response:** Returns health status with document count

#### Get Database Statistics
- **Endpoint:** `GET /api/db-stats`
- **Description:** Get comprehensive statistics including:
  - Total documents count
  - Collection name
  - Disk usage
  - Last updated timestamp

#### Test Database Connection
- **Endpoint:** `GET /api/test-db`
- **Description:** Comprehensive test suite including:
  - Health check
  - Document listing
  - Search functionality
  - Query handler tests

### 2. Document Upload

#### Upload Document File
- **Endpoint:** `POST /api/upload`
- **Method:** Form-data with file upload
- **Supported Formats:** PDF, DOCX, TXT, MD
- **Description:** Uploads a file, automatically chunks it, and stores in ChromaDB
- **Response:** Returns filename, chunks created, and status

#### Upload Document Direct (Text)
- **Endpoint:** `POST /api/upload-direct`
- **Method:** Form-data
- **Parameters:**
  - `text` (required) - Text content
  - `filename` (required) - Filename
  - `file_type` (optional) - File type (default: "text")
  - `source` (optional) - Source identifier (default: "direct_upload")
- **Description:** Upload text directly without chunking (useful for small documents)

#### Upload Text Content (Structured)
- **Endpoint:** `POST /api/upload-text`
- **Method:** Form-data
- **Parameters:**
  - `content` (required) - Text content
  - `title` (required) - Title
  - `description` (optional) - Description
  - `category` (optional) - Category (default: "general")
- **Description:** Upload structured text with metadata

### 3. Document Retrieval

#### List All Documents
- **Endpoint:** `GET /api/documents`
- **Description:** Retrieve all documents with metadata:
  - Filename
  - Chunk count
  - File type
  - Upload date
  - Total size

#### Search Documents (Chat Query)
- **Endpoint:** `POST /api/chat`
- **Method:** JSON
- **Body:**
  ```json
  {
    "message": "What is machine learning?",
    "user_id": "user123",
    "conversation_history": [],
    "mode": "exploration"
  }
  ```
- **Description:** Natural language search with AI-generated response
- **Response:** Includes:
  - AI response
  - Context chunks used
  - Citations
  - LLM provider and model
  - Confidence score

#### Test Query (Simple Search)
- **Endpoint:** `POST /api/test-query`
- **Description:** Simple test endpoint for query processing

### 4. Document Management

#### Delete Document
- **Endpoint:** `DELETE /api/documents/{document_id}`
- **Description:** Delete a document and all its chunks from ChromaDB
- **Note:** Use the filename as `document_id`

### 5. Database Management

#### Backup Database
- **Endpoint:** `POST /api/backup-db`
- **Description:** Create a timestamped backup of the entire database
- **Backup Location:** `backups/chromadb_backup_{timestamp}`

#### Reset Database
- **Endpoint:** `POST /api/reset-db`
- **⚠️ WARNING:** Deletes all data in ChromaDB
- **Recommendation:** Always backup before resetting

## 🔧 Usage Examples

### Example 1: Upload a PDF Document

1. Select **"Upload Document File"** request
2. In the Body tab, select **form-data**
3. Click **Select Files** and choose your PDF
4. Click **Send**
5. Response will show chunks created and status

### Example 2: Search for Information

1. Select **"Search Documents (Chat Query)"** request
2. In the Body tab, modify the JSON:
   ```json
   {
     "message": "Explain neural networks",
     "user_id": "user123",
     "conversation_history": [],
     "mode": "exploration"
   }
   ```
3. Click **Send**
4. Response includes AI-generated answer with citations

### Example 3: List All Documents

1. Select **"List All Documents"** request
2. Click **Send**
3. View all documents with their metadata

### Example 4: Get Database Statistics

1. Select **"Get Database Statistics"** request
2. Click **Send**
3. View total documents, disk usage, and collection info

## 📝 Notes

- **Base URL:** Default is `http://localhost:8000`. Update the `base_url` variable for different environments.
- **Document ID:** When deleting documents, use the exact filename as it appears in the database.
- **File Size Limit:** Maximum file size is 10MB (configurable in backend).
- **Supported File Types:** `.txt`, `.md`, `.pdf`, `.docx`, `.doc`
- **Chunking:** Files uploaded via `/api/upload` are automatically chunked. Use `/api/upload-direct` to skip chunking.

## 🔍 Troubleshooting

### Connection Errors
- Ensure the backend server is running on port 8000
- Check that `base_url` variable is set correctly
- Verify CORS settings if accessing from a different origin

### Upload Failures
- Check file size (max 10MB)
- Verify file format is supported
- Ensure backend has write permissions to `temp_uploads` directory

### Search Not Returning Results
- Verify documents are uploaded successfully
- Check database statistics to confirm documents exist
- Try a broader search query

## 🔗 Related Files

- **Main Collection:** `Ai-Tutor-Postman-Collection.json` - Complete API collection
- **Environment:** `Ai-Tutor-Postman-Environment.json` - Environment variables
- **Backend API Docs:** `http://localhost:8000/docs` - Swagger UI documentation

## 📖 Additional Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- Backend API Swagger UI: `http://localhost:8000/docs`
- Backend API ReDoc: `http://localhost:8000/redoc`

