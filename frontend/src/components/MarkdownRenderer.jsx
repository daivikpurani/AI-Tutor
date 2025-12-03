import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';
import 'katex/dist/katex.min.css';
import 'highlight.js/styles/github.css';

function MarkdownRenderer({ children }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight, rehypeKatex, rehypeRaw]}
      components={{
        code({ inline, className, children: codeChildren, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <pre className="code-block">
              <code className={className} {...props}>
                {codeChildren}
              </code>
            </pre>
          ) : (
            <code className="inline-code" {...props}>
              {codeChildren}
            </code>
          );
        },
        table({ children: tableChildren }) {
          return (
            <div className="table-wrapper">
              <table className="markdown-table">{tableChildren}</table>
            </div>
          );
        },
        blockquote({ children: quoteChildren }) {
          return <blockquote className="markdown-blockquote">{quoteChildren}</blockquote>;
        },
      }}
    >
      {children}
    </ReactMarkdown>
  );
}

export default MarkdownRenderer;


