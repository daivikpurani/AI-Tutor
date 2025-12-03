import React from 'react';
import clsx from 'clsx';
import copy from 'copy-to-clipboard';
import MarkdownRenderer from './MarkdownRenderer';

function ChatBubble({ message, onRetry, onCopy }) {
  const isUser = message.sender === 'user' || message.role === 'user';

  const handleCopy = () => {
    const text = message.text || message.content || '';
    copy(text);
    if (onCopy) onCopy(message);
  };

  return (
    <div className={clsx('message', isUser ? 'user-message' : 'bot-message')}>
      {!isUser && (
        <div className="avatar" aria-hidden>🤖</div>
      )}
      {isUser && (
        <div className="avatar" aria-hidden>👤</div>
      )}
      <div className="message-content">
        {/* Header with optional TL;DR as summary */}
        {message.tldr && (
          <details className="message-collapsible" open>
            <summary className="message-summary">{message.tldr}</summary>
            <div className="message-text">
              <MarkdownRenderer>{message.text || message.content}</MarkdownRenderer>
            </div>
          </details>
        )}

        {!message.tldr && (
          <div className="message-text">
            {isUser ? (
              message.text || message.content
            ) : (
              <MarkdownRenderer>{message.text || message.content}</MarkdownRenderer>
            )}
          </div>
        )}

        {/* Sources hidden for now */}

        <div className="message-footer">
          <div className="message-time">
            {new Date(message.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
          <div className="message-toolbar">
            <button className="toolbar-btn" onClick={handleCopy} title="Copy">
              📋
            </button>
            {!isUser && (
              <button className="toolbar-btn" onClick={() => onRetry && onRetry(message)} title="Retry">
                🔁
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatBubble;


