import React from 'react';
import clsx from 'clsx';

function ChatBubble({ message, onRetry, onCopy }) {
  const isUser = message.sender === 'user' || message.role === 'user';
  const text = message.text || message.content || '';

  return (
    <div className={clsx('message', isUser ? 'user-message' : 'bot-message')}>
      <div className="message-content">
        <div className="message-text">
          {text}
        </div>
      </div>
    </div>
  );
}

export default ChatBubble;

