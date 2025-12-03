import React from 'react';

function Collapsible({ summary, children, defaultOpen = true }) {
  return (
    <details className="collapsible" open={defaultOpen}>
      <summary className="collapsible-summary">{summary}</summary>
      <div className="collapsible-content">{children}</div>
    </details>
  );
}

export default Collapsible;


