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

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const filteredDocuments = documents.filter(doc => {
    const description = doc.description || 'No description available';
    const matchesSearch = doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         description.toLowerCase().includes(searchTerm.toLowerCase());
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

      <div className="docs-main">
        <aside className="docs-sidebar">
          <div className="sidebar-section">
            <div className="sidebar-title">Document Categories</div>
            <div className="sidebar-item active">
              <span className="sidebar-icon">📄</span>
              <span>All Documents</span>
            </div>
            <div className="sidebar-item">
              <span className="sidebar-icon">📚</span>
              <span>Textbooks</span>
            </div>
            <div className="sidebar-item">
              <span className="sidebar-icon">📝</span>
              <span>Notes & Guides</span>
            </div>
            <div className="sidebar-item">
              <span className="sidebar-icon">📊</span>
              <span>Presentations</span>
            </div>
            <div className="sidebar-item">
              <span className="sidebar-icon">📈</span>
              <span>Data & Reports</span>
            </div>
          </div>
          
          <div className="sidebar-section">
            <div className="sidebar-title">Quick Actions</div>
            <div className="sidebar-item">
              <span className="sidebar-icon">🔍</span>
              <span>Search Documents</span>
            </div>
            <div className="sidebar-item">
              <span className="sidebar-icon">📤</span>
              <span>Upload New</span>
            </div>
            <div className="sidebar-item">
              <span className="sidebar-icon">📋</span>
              <span>Export List</span>
            </div>
            <div className="sidebar-item">
              <span className="sidebar-icon">🗂️</span>
              <span>Organize</span>
            </div>
          </div>
          
          <div className="sidebar-section">
            <div className="sidebar-title">Document Stats</div>
            <div className="sidebar-stats">
              <div className="stat-row">
                <span className="stat-label">Total:</span>
                <span className="stat-value">{documents.length}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Chunks:</span>
                <span className="stat-value">{documents.reduce((sum, doc) => sum + (doc.chunk_count || 0), 0)}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Types:</span>
                <span className="stat-value">{new Set(documents.map(doc => doc.file_type)).size}</span>
              </div>
            </div>
          </div>
          
          <div className="sidebar-section">
            <div className="sidebar-title">File Types</div>
            {fileTypes.filter(type => type !== 'all').map(type => (
              <div key={type} className="sidebar-item">
                <span className="sidebar-icon">{getFileTypeIcon(type)}</span>
                <span>{type.toUpperCase()}</span>
                <span className="file-count">
                  ({documents.filter(doc => doc.file_type === type).length})
                </span>
              </div>
            ))}
          </div>
        </aside>

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
                      <span className="file-size">{formatFileSize(doc.total_size)}</span>
                      <span className="upload-date">{formatDate(doc.upload_date)}</span>
                    </div>
                  </div>
                </div>
                
                <div className="document-content">
                  <p className="document-description">{doc.description || 'No description available'}</p>
                  
                  <div className="document-stats">
                    <div className="stat-item">
                      <span className="stat-icon">📄</span>
                      <span className="stat-label">Chunks:</span>
                      <span className="stat-value">{doc.chunk_count || 0}</span>
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
      </div>
    </div>
  );
}

export default Docs;