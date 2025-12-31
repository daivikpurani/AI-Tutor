import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import Docs from './Docs';
import ChatBubble from './components/ChatBubble';
import TypingIndicator from './components/TypingIndicator';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI tutor. I'm ready to help you learn and answer questions about your course materials. What would you like to explore today?",
      sender: 'bot',
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [demoMode, setDemoMode] = useState(false); // Disable demo mode by default
  const [currentPage, setCurrentPage] = useState('chat'); // Track current page
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [mode, setMode] = useState(() => {
    const saved = localStorage.getItem('aiTutorMode');
    return saved === 'assessment' || saved === 'exploration' ? saved : 'exploration';
  });
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const streamBufferRef = useRef('');
  const scrollbarTimeoutRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Auto-hide scrollbar functionality - Smooth fade approach
  const showScrollbar = () => {
    const messagesContainer = document.querySelector('.messages-container');
    const sidebar = document.querySelector('.sidebar');
    
    if (messagesContainer) {
      messagesContainer.classList.remove('scrollbar-hidden');
      messagesContainer.classList.add('scrollbar-visible');
    }
    if (sidebar) {
      sidebar.classList.remove('scrollbar-hidden');
      sidebar.classList.add('scrollbar-visible');
    }
    
    // Clear existing timeout
    if (scrollbarTimeoutRef.current) {
      clearTimeout(scrollbarTimeoutRef.current);
    }
    
    // Set timeout to hide scrollbar after 1.5 seconds (smoother)
    scrollbarTimeoutRef.current = setTimeout(() => {
      if (messagesContainer) {
        messagesContainer.classList.remove('scrollbar-visible');
        messagesContainer.classList.add('scrollbar-hidden');
      }
      if (sidebar) {
        sidebar.classList.remove('scrollbar-visible');
        sidebar.classList.add('scrollbar-hidden');
      }
    }, 1500);
  };

  const hideScrollbar = () => {
    const messagesContainer = document.querySelector('.messages-container');
    const sidebar = document.querySelector('.sidebar');
    
    if (messagesContainer) {
      messagesContainer.classList.remove('scrollbar-visible');
      messagesContainer.classList.add('scrollbar-hidden');
    }
    if (sidebar) {
      sidebar.classList.remove('scrollbar-visible');
      sidebar.classList.add('scrollbar-hidden');
    }
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

  // Persist mode selection
  useEffect(() => {
    try {
      localStorage.setItem('aiTutorMode', mode);
    } catch (_) {}
  }, [mode]);

  // Scrollbar auto-hide effect
  useEffect(() => {
    const handleScroll = () => {
      showScrollbar();
    };

    const handleWheel = () => {
      showScrollbar();
    };

    const handleMouseMove = () => {
      showScrollbar();
    };

    // Add event listeners to multiple elements
    const messagesContainer = document.querySelector('.messages-container');
    const sidebar = document.querySelector('.sidebar');
    
    if (messagesContainer) {
      messagesContainer.addEventListener('scroll', handleScroll, { passive: true });
      messagesContainer.addEventListener('wheel', handleWheel, { passive: true });
    }
    
    if (sidebar) {
      sidebar.addEventListener('scroll', handleScroll, { passive: true });
      sidebar.addEventListener('wheel', handleWheel, { passive: true });
    }
    
    window.addEventListener('scroll', handleScroll, { passive: true });
    window.addEventListener('wheel', handleWheel, { passive: true });
    window.addEventListener('mousemove', handleMouseMove, { passive: true });

    // Initialize scrollbar as visible
    showScrollbar();

    return () => {
      if (messagesContainer) {
        messagesContainer.removeEventListener('scroll', handleScroll);
        messagesContainer.removeEventListener('wheel', handleWheel);
      }
      if (sidebar) {
        sidebar.removeEventListener('scroll', handleScroll);
        sidebar.removeEventListener('wheel', handleWheel);
      }
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('wheel', handleWheel);
      window.removeEventListener('mousemove', handleMouseMove);
      if (scrollbarTimeoutRef.current) {
        clearTimeout(scrollbarTimeoutRef.current);
      }
    };
  }, []);

  const connectWebSocket = () => {
    // Clear any existing reconnect timeout to prevent multiple retries
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Don't try to reconnect if we already have an active connection
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const ws = new WebSocket('ws://localhost:8000/ws/chat');
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
        // Clear any pending reconnect timeout since we're now connected
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
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
        setStatusMessage('');
        
        // Only schedule retry if one isn't already scheduled
        if (!reconnectTimeoutRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectTimeoutRef.current = null;
            connectWebSocket();
          }, 3000);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        // Don't set status here - let onclose handle it
        // onclose will always fire after onerror, so we handle status there
      };

    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnectionStatus('error');
      // Schedule retry even on exception
      if (!reconnectTimeoutRef.current) {
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectTimeoutRef.current = null;
          connectWebSocket();
        }, 3000);
      }
    }
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'processing':
        setIsLoading(true);
        setCurrentStreamingMessage('');
        setStatusMessage('');
        streamBufferRef.current = '';
        break;
      
      case 'context':
        setStatusMessage('🔍 Retrieving relevant information...');
        setCurrentStreamingMessage('');
        streamBufferRef.current = '';
        break;
      
      case 'context_found':
        setStatusMessage(data.message || '📚 Found relevant sections');
        break;
      
      case 'generating':
        setStatusMessage('🤖 Generating response...');
        break;
      
      case 'chunk':
        if (statusMessage) {
          setStatusMessage('');
        }
        setCurrentStreamingMessage(prev => prev + data.content);
        streamBufferRef.current = streamBufferRef.current + data.content;
        break;
      
      case 'complete':
        setStatusMessage('');
        // Finalize the streaming message
        const finalMessage = {
          id: Date.now(),
          text: streamBufferRef.current || currentStreamingMessage,
          sender: 'bot',
          timestamp: new Date().toISOString(),
          tldr: data.tldr || null
        };
        setMessages(prev => [...prev, finalMessage]);
        setCurrentStreamingMessage('');
        streamBufferRef.current = '';
        setIsLoading(false);
        break;
      
      case 'error':
        setStatusMessage('');
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


  // Helper function to send a message
  const sendMessage = async (messageText) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: messageText,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setShowSuggestions(false); // Hide suggestions after first message
    setIsLoading(true);

    // All queries now go to live mode

    try {
      // Send message via WebSocket
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          message: messageText,
          user_id: 'demo-user',
          mode: mode
        }));
      } else {
        // Fallback to HTTP when WebSocket is not connected
        // Canonical backend: FastAPI on http://localhost:8000
        const response = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: messageText,
            user_id: 'demo-user',
            mode: mode
          }),
        });
        const data = await response.json();
        const botMessage = {
          id: Date.now() + 1,
          text: data.response || "I'm processing your question...",
          sender: 'bot',
          timestamp: new Date().toISOString(),
          tldr: data.tldr || null
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

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const messageToSend = inputMessage;
    setInputMessage('');
    await sendMessage(messageToSend);
  };

  const handleRetry = async () => {
    // Retry last user message
    const lastUser = [...messages].reverse().find(m => (m.sender || m.role) === 'user');
    if (lastUser && !isLoading) {
      await sendMessage(lastUser.text || lastUser.content || '');
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
              className={`status-indicator ${connectionStatus}`}
            ></div>
            <span className="status-text">
              {getConnectionStatusText()}
            </span>
          </div>
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
            <ChatBubble key={message.id} message={message} onRetry={handleRetry} />
          ))}
          
          {statusMessage && (
            <div className="status-message">
              {statusMessage}
            </div>
          )}

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
                <TypingIndicator />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {showSuggestions && (
          <div className="demo-suggestions">
            <p>Suggested question to get started:</p>
            <div className="suggestion-buttons">
              {[
                'What is RAGs?'
              ].map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => sendMessage(suggestion)}
                  className="suggestion-button"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

          <form className="input-form" onSubmit={handleSendMessage}>
            <div className="input-container">
              <div className="mode-toggle" aria-label="Response mode">
                <button
                  type="button"
                  className={`mode-chip ${mode === 'assessment' ? 'active' : ''}`}
                  onClick={() => setMode('assessment')}
                >
                  Assessment
                </button>
                <button
                  type="button"
                  className={`mode-chip ${mode === 'exploration' ? 'active' : ''}`}
                  onClick={() => setMode('exploration')}
                >
                  Exploration
                </button>
              </div>
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask me anything about your course material..."
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
