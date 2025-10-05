# Ai-Tutor Postman Collection

This directory contains Postman collection and environment files for testing the Ai-Tutor FastAPI backend.

## Files Included

- `Ai-Tutor-Postman-Collection.json` - Complete API collection
- `Ai-Tutor-Postman-Environment.json` - Environment variables
- `WebSocket-Testing-Guide.md` - WebSocket testing instructions

## Quick Setup

### 1. Import Collection and Environment

1. Open Postman
2. Click **Import** button
3. Select both JSON files:
   - `Ai-Tutor-Postman-Collection.json`
   - `Ai-Tutor-Postman-Environment.json`
4. Select the **Ai-Tutor Development Environment** from the environment dropdown

### 2. Configure Environment Variables

Update the environment variables as needed:

- `base_url`: `http://localhost:8000` (default)
- `user_id`: Your test user ID
- `api_key`: Your OpenAI API key (if needed for authentication)
- `test_file_path`: Path to a test document for upload testing

### 3. Start Your Backend

Make sure your FastAPI backend is running:

```bash
cd backend_python
python main.py
```

The backend should be accessible at `http://localhost:8000`

## Collection Structure

### 📋 Health & Status
- **Root Health Check** (`GET /`) - Basic API information
- **Detailed Health Check** (`GET /api/health`) - Service status

### 💬 Chat & Query
- **Chat Message** (`POST /api/chat`) - Send chat messages
- **Chat with History** (`POST /api/chat`) - Chat with conversation context
- **Test Query** (`POST /api/test-query`) - Test query processing

### 📄 Document Management
- **Upload Document** (`POST /api/upload`) - Upload and process documents
- **List Documents** (`GET /api/documents`) - List all uploaded documents
- **Delete Document** (`DELETE /api/documents/{id}`) - Remove documents

### 🔧 Testing & Debug
- **Test Database Connection** (`GET /api/test-db`) - Comprehensive system test

### 📚 API Documentation
- **Swagger UI** (`GET /docs`) - Interactive API documentation
- **ReDoc Documentation** (`GET /redoc`) - Alternative documentation

## Usage Examples

### Testing Chat Functionality

1. Select **Chat & Query** → **Chat Message**
2. Update the request body:
   ```json
   {
     "message": "What is machine learning?",
     "user_id": "test_user_123",
     "conversation_history": []
   }
   ```
3. Click **Send**
4. Check the response for AI-generated content

### Testing Document Upload

1. Select **Document Management** → **Upload Document**
2. In the **Body** tab, select **form-data**
3. Add a file to the `file` field
4. Click **Send**
5. Verify the document was processed and chunks were created

### Testing Database Connection

1. Select **Testing & Debug** → **Test Database Connection**
2. Click **Send**
3. Review the comprehensive test results
4. Check that all services are healthy

## WebSocket Testing

Since Postman has limited WebSocket support, use the methods described in `WebSocket-Testing-Guide.md`:

- Browser console testing
- Command line with `wscat`
- Python script testing
- Limited Postman WebSocket support

## Environment Variables

### Development Environment
- `base_url`: `http://localhost:8000`
- `frontend_url`: `http://localhost:3000`
- `websocket_url`: `ws://localhost:8000/ws/chat`

### Production Environment (when available)
- `base_url_production`: `https://your-production-domain.com`

### Test Variables
- `user_id`: `test_user_123`
- `document_id`: `sample_document_id`
- `test_message`: `What is machine learning?`

## Common Test Scenarios

### 1. Complete Workflow Test
1. **Health Check** - Verify API is running
2. **Upload Document** - Add a test document
3. **List Documents** - Verify upload succeeded
4. **Chat Message** - Ask about uploaded content
5. **Test Database** - Verify all systems working

### 2. Error Handling Test
1. Send invalid JSON to chat endpoint
2. Upload unsupported file type
3. Try to delete non-existent document
4. Test with missing required fields

### 3. Performance Test
1. Upload large document
2. Send multiple concurrent chat requests
3. Test WebSocket with rapid messages
4. Monitor response times

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure backend is running on port 8000
   - Check `base_url` environment variable

2. **CORS Errors**
   - Verify CORS configuration in FastAPI
   - Check allowed origins include Postman

3. **File Upload Issues**
   - Ensure file path is correct
   - Check file size limits
   - Verify supported file types

4. **WebSocket Connection Failed**
   - Use WebSocket testing guide
   - Check if WebSocket endpoint is enabled
   - Verify WebSocket URL format

### Debug Tips

1. **Enable Request/Response Logging**
   - Use Postman Console to see detailed logs
   - Check browser Network tab for WebSocket connections

2. **Test Individual Components**
   - Start with health check
   - Test database connection
   - Verify document upload
   - Test chat functionality

3. **Check Backend Logs**
   - Monitor FastAPI console output
   - Check for error messages
   - Verify ChromaDB connection

## API Response Examples

### Successful Chat Response
```json
{
  "response": "Machine learning is a subset of artificial intelligence...",
  "query": "What is machine learning?",
  "user_id": "test_user_123",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "context_chunks_used": 3,
  "status": "success"
}
```

### Successful Upload Response
```json
{
  "message": "Successfully processed document.pdf",
  "filename": "document.pdf",
  "chunks_created": 15,
  "status": "success"
}
```

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "services": {
    "vector_db": "healthy",
    "query_handler": "healthy"
  }
}
```

## Contributing

When adding new endpoints to the API:

1. Update the Postman collection
2. Add example requests and responses
3. Update environment variables if needed
4. Test all scenarios
5. Update this README

## Support

For issues with the Postman collection:
1. Check the WebSocket testing guide
2. Verify environment variables
3. Ensure backend is running
4. Check API documentation at `/docs`

---

*Last updated: January 2024*
*Version: 1.0.0*
