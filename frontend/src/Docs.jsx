import React, { useState, useEffect } from 'react';
import './Docs.css';

function Docs() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');

  // Fetch uploaded documents from the backend
  useEffect(() => {
    fetchDocuments();
    
    // Auto-refresh every 30 seconds to check for new documents
    const interval = setInterval(fetchDocuments, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/documents');
      if (!response.ok) {
        throw new Error('Failed to fetch documents');
      }
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (err) {
      setError(err.message);
      // Set empty array instead of sample data
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  const getFileTypeIcon = (fileType) => {
    const icons = {
      pdf: '📄',
      docx: '📝',
      doc: '📝',
      txt: '📃',
      md: '📋',
      pptx: '📊',
      ppt: '📊',
      xlsx: '📈',
      xls: '📈'
    };
    return icons[fileType] || '📄';
  };

  const getFileTypeColor = (fileType) => {
    const colors = {
      pdf: '#E53E3E',
      docx: '#3182CE',
      doc: '#3182CE',
      txt: '#38A169',
      md: '#805AD5',
      pptx: '#D69E2E',
      ppt: '#D69E2E',
      xlsx: '#38A169',
      xls: '#38A169'
    };
    return colors[fileType] || '#718096';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === 'all' || doc.file_type === filterType;
    return matchesSearch && matchesFilter;
  });

  const fileTypes = ['all', ...new Set(documents.map(doc => doc.file_type))];

  const handleFileUpload = async (event) => {
    const files = event.target.files;
    if (!files.length) return;

    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('http://localhost:8000/api/upload', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          // Refresh the documents list after successful upload
          await fetchDocuments();
        } else {
          console.error('Upload failed for:', file.name);
        }
      } catch (error) {
        console.error('Upload error:', error);
      }
    }

    // Reset the file input
    event.target.value = '';
  };

  if (loading) {
    return (
      <div className="docs-container">
        <div className="docs-header">
          <div className="docs-title">
            <h1>Course Materials</h1>
            <p>Educational documents and resources uploaded to the system</p>
          </div>
        </div>
        <div className="docs-content">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading course materials...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="docs-container">
      <div className="docs-header">
        <div className="docs-title">
          <h1>Course Materials</h1>
          <p>Educational documents and resources uploaded to the system</p>
        </div>
      </div>

      <div className="docs-content">
        {/* Search and Filter Controls */}
        <div className="docs-controls">
          <div className="search-container">
            <input
              type="text"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <span className="search-icon">🔍</span>
          </div>
          
          <div className="filter-container">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="filter-select"
            >
              {fileTypes.map(type => (
                <option key={type} value={type}>
                  {type === 'all' ? 'All Types' : type.toUpperCase()}
                </option>
              ))}
            </select>
          </div>
          
          <button 
            onClick={fetchDocuments}
            className="refresh-button"
            title="Refresh documents list"
          >
            🔄 Refresh
          </button>
        </div>

        {/* Documents Grid */}
        {error && (
          <div className="error-message">
            <p>⚠️ {error}</p>
            <p>Unable to connect to the backend. Please make sure the server is running.</p>
          </div>
        )}

        <div className="documents-grid">
          {filteredDocuments.length === 0 ? (
            <div className="no-documents">
              <div className="no-docs-icon">📭</div>
              <h3>No documents found</h3>
              <p>
                {searchTerm || filterType !== 'all' 
                  ? 'Try adjusting your search or filter criteria.'
                  : 'No course materials have been uploaded yet. Upload documents to get started!'
                }
              </p>
            </div>
          ) : (
            filteredDocuments.map((doc) => (
              <div key={doc.id} className="document-card">
                <div className="document-header">
                  <div 
                    className="document-type-icon"
                    style={{ backgroundColor: getFileTypeColor(doc.file_type) }}
                  >
                    {getFileTypeIcon(doc.file_type)}
                  </div>
                  <div className="document-info">
                    <h3 className="document-title">{doc.filename}</h3>
                    <div className="document-meta">
                      <span className="file-type">{doc.file_type.toUpperCase()}</span>
                      <span className="file-size">{doc.file_size}</span>
                      <span className="upload-date">{formatDate(doc.upload_date)}</span>
                    </div>
                  </div>
                </div>
                
                <div className="document-content">
                  <p className="document-description">{doc.description}</p>
                  
                  <div className="document-stats">
                    <div className="stat-item">
                      <span className="stat-icon">📄</span>
                      <span className="stat-label">Chunks:</span>
                      <span className="stat-value">{doc.chunks_count}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-icon">🔍</span>
                      <span className="stat-label">Searchable:</span>
                      <span className="stat-value">Yes</span>
                    </div>
                  </div>
                  
                  <div className="document-actions">
                    <button className="action-button primary">
                      <span>👁️</span>
                      View Content
                    </button>
                    <button className="action-button secondary">
                      <span>💬</span>
                      Ask About This
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Upload Section */}
        <div className="upload-section">
          <div className="upload-card">
            <div className="upload-icon">📤</div>
            <h3>Upload New Course Material</h3>
            <p>Add new documents to expand the knowledge base</p>
            <input
              type="file"
              id="file-upload"
              multiple
              accept=".pdf,.docx,.doc,.txt,.md,.pptx,.ppt"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
            />
            <label htmlFor="file-upload" className="upload-button">
              Choose Files
            </label>
            <div className="supported-formats">
              <small>Supported: PDF, DOCX, TXT, MD, PPTX</small>
            </div>
          </div>
        </div>
      </div>

      <div className="docs-footer">
        <div className="docs-summary">
          <h3>Course Materials Summary</h3>
          <div className="summary-stats">
            <div className="summary-item">
              <span className="summary-number">{documents.length}</span>
              <span className="summary-label">Total Documents</span>
            </div>
            <div className="summary-item">
              <span className="summary-number">
                {documents.reduce((sum, doc) => sum + doc.chunks_count, 0)}
              </span>
              <span className="summary-label">Total Chunks</span>
            </div>
            <div className="summary-item">
              <span className="summary-number">
                {new Set(documents.map(doc => doc.file_type)).size}
              </span>
              <span className="summary-label">File Types</span>
            </div>
          </div>
        </div>
        
        <div className="docs-info">
          <h3>About Course Materials</h3>
          <p>
            These are the educational documents that have been uploaded to the AI-Tutor system. 
            The AI can reference and answer questions based on the content of these materials. 
            Each document is processed and chunked for efficient search and retrieval.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Docs;