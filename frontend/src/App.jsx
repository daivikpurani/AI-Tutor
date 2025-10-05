import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import './App.css';
import 'highlight.js/styles/github.css'; // Code highlighting theme
import Docs from './Docs';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI tutor. How can I help you learn today?",
      sender: 'bot',
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');
  const [demoMode, setDemoMode] = useState(true); // Enable demo mode by default
  const [currentPage, setCurrentPage] = useState('chat'); // Track current page
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const streamBufferRef = useRef('');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStreamingMessage]);

  // WebSocket connection management
  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket('ws://localhost:8000/ws/chat');
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setConnectionStatus('disconnected');
        setIsLoading(false);
        setCurrentStreamingMessage('');
        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
        setIsLoading(false);
        setCurrentStreamingMessage('');
      };

    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnectionStatus('error');
    }
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'processing':
        setIsLoading(true);
        setCurrentStreamingMessage('');
        streamBufferRef.current = '';
        break;
      
      case 'context':
        setCurrentStreamingMessage('🔍 Retrieving relevant information...');
        break;
      
      case 'context_found':
        setCurrentStreamingMessage(`📚 Found ${data.message.split(' ')[1]} relevant sections`);
        break;
      
      case 'generating':
        setCurrentStreamingMessage('🤖 Generating response...');
        break;
      
      case 'chunk':
        setCurrentStreamingMessage(prev => prev + data.content);
        streamBufferRef.current = streamBufferRef.current + data.content;
        break;
      
      case 'complete':
        // Finalize the streaming message
        const finalMessage = {
          id: Date.now(),
          text: streamBufferRef.current || currentStreamingMessage,
          sender: 'bot',
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, finalMessage]);
        setCurrentStreamingMessage('');
        streamBufferRef.current = '';
        setIsLoading(false);
        break;
      
      case 'error':
        const errorMessage = {
          id: Date.now(),
          text: data.message || "Sorry, I'm having trouble connecting. Please try again.",
          sender: 'bot',
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, errorMessage]);
        setCurrentStreamingMessage('');
        setIsLoading(false);
        break;
      
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  // Demo mode function for presentation
  const simulateStreamingResponse = async (query) => {
    const demoResponses = {
      "what is web development": `# Web Development Overview

Web development is the discipline of designing, building, and maintaining websites and web applications that run in a browser.

## Main Areas

### 1. Front-end Development
- **Focus**: User interface and experience
- **Technologies**: HTML, CSS, JavaScript
- **Purpose**: Structure, presentation, and interactivity

### 2. Back-end Development  
- **Focus**: Business logic, data storage, authentication
- **Technologies**: Servers, databases, frameworks
- **Purpose**: APIs and server-side processing

### 3. DevOps/Deployment
- **Focus**: Hosting, CI/CD, monitoring, scalability
- **Platforms**: Vercel, Netlify, cloud providers

## Key Principles

- **Accessibility**: Inclusive design and semantic HTML
- **Performance**: Fast loading and responsive rendering  
- **Security**: Input validation, authentication, HTTPS
- **SEO**: Crawlability and metadata

## Common Tech Stacks

\`\`\`javascript
// Frontend Example
const App = () => {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    fetch('/api/data')
      .then(res => res.json())
      .then(setData);
  }, []);
  
  return <div>{data.map(item => <Item key={item.id} {...item} />)}</div>;
};
\`\`\`

**Backend**: Node.js, Python, Go, Java  
**APIs**: REST, GraphQL  
**Databases**: PostgreSQL, MySQL, MongoDB

> The goal is to deliver reliable, accessible, and maintainable experiences across devices and network conditions.`,

      "what is machine learning": `# Machine Learning Fundamentals

Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.

## Types of Machine Learning

### 1. Supervised Learning
- **Definition**: Learning from labeled examples
- **Examples**: Classification, regression
- **Use Cases**: Email spam detection, price prediction

### 2. Unsupervised Learning  
- **Definition**: Finding patterns in unlabeled data
- **Examples**: Clustering, dimensionality reduction
- **Use Cases**: Customer segmentation, anomaly detection

### 3. Reinforcement Learning
- **Definition**: Learning through trial and error with rewards
- **Examples**: Game playing, robotics
- **Use Cases**: Autonomous vehicles, recommendation systems

## Key Concepts

\`\`\`python
# Example: Simple Linear Regression
from sklearn.linear_model import LinearRegression
import numpy as np

# Training data
X = np.array([[1], [2], [3], [4]])
y = np.array([2, 4, 6, 8])

# Train model
model = LinearRegression()
model.fit(X, y)

# Make prediction
prediction = model.predict([[5]])
print(f"Prediction: {prediction[0]}")  # Output: 10.0
\`\`\`

**Key Benefits:**
- Automated decision making
- Pattern recognition in large datasets
- Continuous improvement through experience`,

      "explain ai": `# Artificial Intelligence (AI)

AI refers to the simulation of human intelligence in machines that are programmed to think and learn like humans.

## Core Technologies

| Technology | Description | Applications |
|------------|-------------|--------------|
| **Machine Learning** | Algorithms that learn from data | Predictive analytics, recommendation systems |
| **Natural Language Processing** | Understanding and generating human language | Chatbots, translation, sentiment analysis |
| **Computer Vision** | Interpreting visual information | Image recognition, autonomous vehicles |
| **Robotics** | Physical AI systems | Manufacturing, healthcare, exploration |

## AI Capabilities

### Cognitive Functions
- ✅ **Visual Perception**: Image and video analysis
- ✅ **Speech Recognition**: Converting speech to text  
- ✅ **Decision Making**: Strategic planning and optimization
- ✅ **Language Translation**: Cross-language communication

## Real-World Applications

\`\`\`python
# Example: Simple AI Chatbot
import openai

def chat_with_ai(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message.content

# Usage
user_input = "Explain quantum computing"
ai_response = chat_with_ai(user_input)
print(ai_response)
\`\`\`

> **Note**: AI systems are becoming increasingly sophisticated and are transforming industries from healthcare to finance through intelligent automation and data-driven decision making.`,

      "how do neural networks work": `# Neural Networks Explained

Neural networks are computing systems inspired by biological neural networks in the human brain.

## Architecture Overview

### Basic Structure
- **Input Layer**: Receives data
- **Hidden Layers**: Process information  
- **Output Layer**: Produces results

\`\`\`python
# Simple Neural Network Example
import tensorflow as tf
from tensorflow import keras

# Create a simple neural network
model = keras.Sequential([
    keras.layers.Dense(128, activation='relu', input_shape=(784,)),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(10, activation='softmax')
])

# Compile the model
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Train the model
model.fit(x_train, y_train, epochs=5, validation_data=(x_test, y_test))
\`\`\`

## How It Works

### 1. **Forward Propagation**
- Data flows from input → hidden → output layers
- Each neuron processes inputs using weights and biases
- Activation functions determine neuron output

### 2. **Training Process**
- **Backpropagation**: Adjusts weights based on errors
- **Gradient Descent**: Minimizes loss function
- **Iterative Learning**: Improves accuracy over time

## Key Components

| Component | Purpose | Example |
|-----------|---------|---------|
| **Weights** | Connection strength between neurons | 0.5, -0.3, 1.2 |
| **Biases** | Offset values for activation | +0.1, -0.2 |
| **Activation Functions** | Non-linear transformations | ReLU, Sigmoid, Tanh |

## Applications

- 🧠 **Image Recognition**: Identifying objects in photos
- 🗣️ **Speech Processing**: Voice commands and transcription  
- 📈 **Predictive Analytics**: Forecasting trends and patterns
- 🎮 **Game AI**: Strategic decision making

> Neural networks excel at finding complex patterns in data that would be difficult for traditional algorithms to detect.`
    };

    const normalizedQuery = query.toLowerCase().trim();
    let response = demoResponses[normalizedQuery] || 
      "That's a great question! AI and machine learning are fascinating topics. Machine learning allows computers to learn from data without explicit programming, while neural networks mimic how the human brain processes information. These technologies are revolutionizing industries from healthcare to finance by enabling intelligent automation and data-driven decision making.";

    // Simulate streaming by sending chunks
    setCurrentStreamingMessage('');
    streamBufferRef.current = '';
    const words = response.split(' ');
    const chunkSize = 3;
    
    for (let i = 0; i < words.length; i += chunkSize) {
      const chunk = words.slice(i, i + chunkSize).join(' ') + ' ';
      setCurrentStreamingMessage(prev => prev + chunk);
      streamBufferRef.current = streamBufferRef.current + chunk;
      await new Promise(resolve => setTimeout(resolve, 150)); // 150ms delay between chunks
    }

    // Complete the response
    setTimeout(() => {
      const finalMessage = {
        id: Date.now(),
        text: streamBufferRef.current,
        sender: 'bot',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, finalMessage]);
      setCurrentStreamingMessage('');
      streamBufferRef.current = '';
      setIsLoading(false);
    }, 500);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    // Demo mode - simulate streaming response
    if (demoMode) {
      await simulateStreamingResponse(messageToSend);
      return;
    }

    try {
      // Send message via WebSocket
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          message: messageToSend,
          user_id: 'demo-user'
        }));
      } else {
        // Fallback to HTTP when WebSocket is not connected
        const response = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: messageToSend,
            user_id: 'demo-user'
          }),
        });
        const data = await response.json();
        const botMessage = {
          id: Date.now() + 1,
          text: data.response || "I'm processing your question...",
          sender: 'bot',
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, botMessage]);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "Sorry, I'm having trouble connecting. Please try again.",
        sender: 'bot',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return '#4CAF50';
      case 'disconnected': return '#FF9800';
      case 'error': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'disconnected': return 'Connecting...';
      case 'error': return 'Connection Error';
      default: return 'Unknown';
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <div className="logo">
            <div className="logo-icon">🧠</div>
            <span>Ai-Tutor</span>
          </div>
          <nav className="header-nav">
            <button 
              onClick={() => setCurrentPage('chat')} 
              className={`nav-item ${currentPage === 'chat' ? 'active' : ''}`}
            >
              Chat
            </button>
            <button 
              onClick={() => setCurrentPage('docs')} 
              className={`nav-item ${currentPage === 'docs' ? 'active' : ''}`}
            >
              Docs
            </button>
            <button 
              onClick={() => setCurrentPage('settings')} 
              className={`nav-item ${currentPage === 'settings' ? 'active' : ''}`}
            >
              Settings
            </button>
          </nav>
        </div>
        <div className="header-right">
          <div className="connection-status">
            <div 
              className={`status-indicator ${demoMode ? 'demo' : connectionStatus}`}
            ></div>
            <span className="status-text">
              {demoMode ? 'Demo Mode' : getConnectionStatusText()}
            </span>
          </div>
          <button 
            className="demo-toggle"
            onClick={() => setDemoMode(!demoMode)}
          >
            {demoMode ? 'Live Mode' : 'Demo Mode'}
          </button>
        </div>
      </header>

      <main className="main-content">
        {currentPage === 'chat' && (
          <>
            <aside className="sidebar">
              <div className="sidebar-section">
                <div className="sidebar-title">Navigation</div>
                <div className="sidebar-item active">
                  <span className="sidebar-icon">💬</span>
                  <span>New Chat</span>
                </div>
                <div className="sidebar-item">
                  <span className="sidebar-icon">📚</span>
                  <span>Learning History</span>
                </div>
                <div className="sidebar-item">
                  <span className="sidebar-icon">📊</span>
                  <span>Progress</span>
                </div>
              </div>
              
              <div className="sidebar-section">
                <div className="sidebar-title">Quick Actions</div>
                <div className="sidebar-item">
                  <span className="sidebar-icon">🔍</span>
                  <span>Search Topics</span>
                </div>
                <div className="sidebar-item">
                  <span className="sidebar-icon">📝</span>
                  <span>Study Notes</span>
                </div>
                <div className="sidebar-item">
                  <span className="sidebar-icon">🎯</span>
                  <span>Practice Tests</span>
                </div>
              </div>
              
              <div className="sidebar-section">
                <div className="sidebar-title">Settings</div>
                <div className="sidebar-item">
                  <span className="sidebar-icon">⚙️</span>
                  <span>Preferences</span>
                </div>
                <div className="sidebar-item">
                  <span className="sidebar-icon">ℹ️</span>
                  <span>Help & Support</span>
                </div>
              </div>
              
              <div className="sidebar-section">
                <div className="sidebar-title">Database</div>
                <div className="sidebar-item" onClick={() => window.open('http://localhost:8000/api/documents', '_blank')}>
                  <span className="sidebar-icon">🗄️</span>
                  <span>View ChromaDB Docs</span>
                </div>
                <div className="sidebar-item" onClick={() => window.open('http://localhost:8000/docs', '_blank')}>
                  <span className="sidebar-icon">📚</span>
                  <span>API Documentation</span>
                </div>
              </div>
            </aside>
        
        <div className="chat-container">
          <div className="messages-container">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
            >
              <div className="message-content">
                <div className="message-text">
                  {message.sender === 'bot' ? (
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      rehypePlugins={[rehypeHighlight, rehypeRaw]}
                      components={{
                        code({node, inline, className, children, ...props}) {
                          const match = /language-(\w+)/.exec(className || '');
                          return !inline && match ? (
                            <pre className="code-block">
                              <code className={className} {...props}>
                                {children}
                              </code>
                            </pre>
                          ) : (
                            <code className="inline-code" {...props}>
                              {children}
                            </code>
                          );
                        },
                        table({children}) {
                          return <div className="table-wrapper"><table className="markdown-table">{children}</table></div>;
                        },
                        blockquote({children}) {
                          return <blockquote className="markdown-blockquote">{children}</blockquote>;
                        }
                      }}
                    >
                      {message.text}
                    </ReactMarkdown>
                  ) : (
                    message.text
                  )}
                </div>
                <div className="message-time">{formatTime(message.timestamp)}</div>
              </div>
            </div>
          ))}
          
          {/* Streaming message display */}
          {currentStreamingMessage && (
            <div className="message bot-message streaming-message">
              <div className="message-content">
                <div className="message-text">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeHighlight, rehypeRaw]}
                    components={{
                      code({node, inline, className, children, ...props}) {
                        const match = /language-(\w+)/.exec(className || '');
                        return !inline && match ? (
                          <pre className="code-block">
                            <code className={className} {...props}>
                              {children}
                            </code>
                          </pre>
                        ) : (
                          <code className="inline-code" {...props}>
                            {children}
                          </code>
                        );
                      },
                      table({children}) {
                        return <div className="table-wrapper"><table className="markdown-table">{children}</table></div>;
                      },
                      blockquote({children}) {
                        return <blockquote className="markdown-blockquote">{children}</blockquote>;
                      }
                    }}
                  >
                    {currentStreamingMessage}
                  </ReactMarkdown>
                  <span className="streaming-cursor">|</span>
                </div>
              </div>
            </div>
          )}
          
          {/* Loading indicator when no streaming message */}
          {isLoading && !currentStreamingMessage && (
            <div className="message bot-message">
              <div className="message-content">
                <div className="message-text">
                  <span className="typing-indicator">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="demo-suggestions">
          <p>{demoMode ? 'Try these demo questions:' : 'Suggested questions to get started:'}</p>
          <div className="suggestion-buttons">
            {(demoMode ? [
              'What is machine learning?', 
              'Explain AI', 
              'How do neural networks work?', 
              'What is web development?'
            ] : [
              'What topics can you help me learn?',
              'How does this AI tutoring system work?',
              'Can you explain a concept step by step?',
              'What study materials do you have?',
              'Help me understand a difficult topic',
              'Create a study plan for me'
            ]).map((suggestion, index) => (
              <button
                key={index}
                onClick={() => setInputMessage(suggestion)}
                className="suggestion-button"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

          <form className="input-form" onSubmit={handleSendMessage}>
            <div className="input-container">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder={demoMode ? "Try the demo questions above or ask anything..." : "Ask me anything about your course material..."}
                className="message-input"
                disabled={isLoading}
              />
              <button
                type="submit"
                className="send-button"
                disabled={!inputMessage.trim() || isLoading}
              >
                {isLoading ? '⏳' : '📤'}
              </button>
            </div>
          </form>
        </div>
          </>
        )}
        
        {currentPage === 'docs' && <Docs />}
        
        {currentPage === 'settings' && (
          <div className="settings-container">
            <div className="settings-content">
              <h2>⚙️ Settings</h2>
              <p>Settings page coming soon...</p>
            </div>
          </div>
        )}
      </main>

    </div>
  );
}

export default App;
