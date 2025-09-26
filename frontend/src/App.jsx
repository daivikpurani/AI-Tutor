import React, { useState, useRef, useEffect } from 'react';
import './App.css';

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
      const ws = new WebSocket('ws://localhost:8001/ws/chat');
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
      "what is machine learning": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It involves algorithms that can identify patterns in data and make predictions or decisions based on that data. There are three main types: supervised learning (learning from labeled examples), unsupervised learning (finding patterns in unlabeled data), and reinforcement learning (learning through trial and error with rewards).",
      "explain ai": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. It encompasses various technologies including machine learning, natural language processing, computer vision, and robotics. AI systems can perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and language translation.",
      "how do neural networks work": "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) organized in layers. Information flows through the network, with each neuron processing inputs and passing results to the next layer. During training, the network adjusts connection weights to minimize errors. This allows the network to learn complex patterns and make accurate predictions on new data."
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
        const response = await fetch('http://localhost:8001/api/chat', {
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
        <h1>🧠 Ai-Tutor</h1>
        <p>Your intelligent learning assistant</p>
        <div className="connection-status">
          <div 
            className="status-indicator" 
            style={{ backgroundColor: demoMode ? '#9C27B0' : getConnectionStatusColor() }}
          ></div>
          <span className="status-text">
            {demoMode ? 'Demo Mode' : getConnectionStatusText()}
          </span>
          <button 
            className="demo-toggle"
            onClick={() => setDemoMode(!demoMode)}
            style={{ 
              marginLeft: '10px', 
              padding: '2px 8px', 
              fontSize: '0.7rem',
              borderRadius: '4px',
              border: '1px solid rgba(255,255,255,0.3)',
              background: 'rgba(255,255,255,0.1)',
              color: 'white',
              cursor: 'pointer'
            }}
          >
            {demoMode ? 'Live Mode' : 'Demo Mode'}
          </button>
        </div>
      </header>

      <main className="chat-container">
        <div className="messages-container">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
            >
              <div className="message-content">
                <div className="message-text">{message.text}</div>
                <div className="message-time">{formatTime(message.timestamp)}</div>
              </div>
            </div>
          ))}
          
          {/* Streaming message display */}
          {currentStreamingMessage && (
            <div className="message bot-message streaming-message">
              <div className="message-content">
                <div className="message-text">
                  {currentStreamingMessage}
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

        {demoMode && (
          <div className="demo-suggestions">
            <p style={{ fontSize: '0.8rem', color: '#666', margin: '0.5rem 0', textAlign: 'center' }}>
              Try these demo questions:
            </p>
            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '1rem' }}>
              {['What is machine learning?', 'Explain AI', 'How do neural networks work?'].map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setInputMessage(suggestion)}
                  style={{
                    padding: '0.3rem 0.6rem',
                    fontSize: '0.7rem',
                    borderRadius: '12px',
                    border: '1px solid #e0e0e0',
                    background: '#f5f5f5',
                    color: '#333',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.background = '#e0e0e0';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.background = '#f5f5f5';
                  }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

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
      </main>

      <footer className="app-footer">
        <p>Ai-Tutor v1.0.0 - Research Project</p>
      </footer>
    </div>
  );
}

export default App;
