# WebSocket Testing Guide for Ai-Tutor

Since Postman has limited WebSocket support, here are alternative methods to test the WebSocket endpoints:

## WebSocket Endpoint: `ws://localhost:8000/ws/chat`

### Method 1: Browser Console Testing

Open your browser's developer console and run:

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/chat');

// Handle connection open
ws.onopen = function(event) {
    console.log('WebSocket connected');
    
    // Send a test message
    const message = {
        message: "Hello, can you help me understand machine learning?",
        user_id: "test_user_123"
    };
    
    ws.send(JSON.stringify(message));
};

// Handle incoming messages
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    
    if (data.type === 'processing') {
        console.log('AI is processing your question...');
    } else if (data.type === 'response') {
        console.log('AI Response:', data.message);
    } else if (data.type === 'streaming') {
        console.log('Streaming response:', data.content);
    }
};

// Handle connection close
ws.onclose = function(event) {
    console.log('WebSocket disconnected');
};

// Handle errors
ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};

// Close connection when done
// ws.close();
```

### Method 2: Using wscat (Command Line Tool)

Install wscat:
```bash
npm install -g wscat
```

Connect and test:
```bash
# Connect to WebSocket
wscat -c ws://localhost:8000/ws/chat

# Send a message (paste this in the terminal)
{"message": "What is artificial intelligence?", "user_id": "test_user"}

# Send another message
{"message": "Can you explain neural networks?", "user_id": "test_user"}
```

### Method 3: Using Python Script

Create a test script `test_websocket.py`:

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/chat"
    
    async with websockets.connect(uri) as websocket:
        # Send a test message
        message = {
            "message": "Hello, can you help me with machine learning concepts?",
            "user_id": "python_test_user"
        }
        
        await websocket.send(json.dumps(message))
        print("Sent:", message)
        
        # Listen for responses
        async for response in websocket:
            data = json.loads(response)
            print("Received:", data)
            
            if data.get("type") == "response":
                print("Final response received")
                break

# Run the test
asyncio.run(test_websocket())
```

Run the script:
```bash
pip install websockets
python test_websocket.py
```

### Method 4: Using Postman WebSocket (Limited)

1. Open Postman
2. Create a new WebSocket request
3. Enter URL: `ws://localhost:8000/ws/chat`
4. Click "Connect"
5. Send message:
```json
{
  "message": "What is deep learning?",
  "user_id": "postman_user"
}
```

### Expected WebSocket Message Flow

1. **Connection**: WebSocket connects successfully
2. **Processing Message**: 
   ```json
   {
     "type": "processing",
     "message": "Processing your question...",
     "timestamp": "2024-01-01T12:00:00.000Z"
   }
   ```
3. **Streaming Response** (multiple messages):
   ```json
   {
     "type": "streaming",
     "content": "Deep learning is a subset of machine learning...",
     "timestamp": "2024-01-01T12:00:01.000Z"
   }
   ```
4. **Final Response**:
   ```json
   {
     "type": "response",
     "message": "Complete response here...",
     "timestamp": "2024-01-01T12:00:05.000Z",
     "context_chunks_used": 3
   }
   ```

### Testing Scenarios

#### Scenario 1: Basic Chat
```json
{
  "message": "What is machine learning?",
  "user_id": "user123"
}
```

#### Scenario 2: Follow-up Question
```json
{
  "message": "Can you give me an example?",
  "user_id": "user123"
}
```

#### Scenario 3: Complex Query
```json
{
  "message": "Explain the difference between supervised and unsupervised learning with examples",
  "user_id": "user123"
}
```

#### Scenario 4: Document-Specific Query
```json
{
  "message": "What does the uploaded PDF say about neural networks?",
  "user_id": "user123"
}
```

### Troubleshooting WebSocket Issues

1. **Connection Refused**: Ensure backend is running on port 8000
2. **CORS Issues**: Check CORS configuration in FastAPI
3. **Message Format**: Ensure JSON is properly formatted
4. **Timeout**: WebSocket may timeout after inactivity

### WebSocket vs REST API Comparison

| Feature | REST API | WebSocket |
|---------|----------|-----------|
| **Connection** | Stateless | Persistent |
| **Response Time** | Single response | Streaming |
| **Real-time** | No | Yes |
| **Use Case** | Simple queries | Interactive chat |
| **Testing** | Easy with Postman | Requires special tools |

### Integration with Frontend

The frontend should handle WebSocket connections like this:

```javascript
class ChatWebSocket {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    connect() {
        this.ws = new WebSocket('ws://localhost:8000/ws/chat');
        
        this.ws.onopen = () => {
            console.log('Connected to chat');
            this.reconnectAttempts = 0;
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            this.handleReconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    sendMessage(message, userId) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                message: message,
                user_id: userId
            }));
        }
    }
    
    handleMessage(data) {
        // Handle different message types
        switch(data.type) {
            case 'processing':
                this.showProcessingIndicator();
                break;
            case 'streaming':
                this.appendToResponse(data.content);
                break;
            case 'response':
                this.showCompleteResponse(data.message);
                break;
        }
    }
    
    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => this.connect(), 1000 * this.reconnectAttempts);
        }
    }
}
```
