import { useState } from 'react';
import '../styles/upload-table.css';

const UploadTable = ({ files }) => {
  const [expandedRows, setExpandedRows] = useState(new Set());

  const toggleExpand = (index) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedRows(newExpanded);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const truncateHash = (hash, length = 16) => {
    if (!hash) return 'N/A';
    return hash.length > length ? `${hash.substring(0, length)}...` : hash;
  };

  if (files.length === 0) {
    return (
      <div className="empty-table">
        <p>No files uploaded yet</p>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="upload-table">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Hash</th>
            <th>Record ID</th>
            <th>Status</th>
            <th>TX Hash</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file, index) => (
            <tr key={index}>
              <td className="filename-col">{file.filename}</td>
              <td>
                <span className="hash-text">{truncateHash(file.hash)}</span>
                <button
                  className="copy-btn-small"
                  onClick={() => copyToClipboard(file.hash)}
                  title="Copy hash"
                >
                  📋
                </button>
              </td>
              <td className="mono">{file.recordId || 'N/A'}</td>
              <td>
                <span className={`status-badge-small ${file.status}`}>
                  {file.status === 'success' && '✓ Success'}
                  {file.status === 'error' && '✗ Error'}
                  {file.status === 'processing' && '⏳ Processing'}
                </span>
              </td>
              <td>
                <span className="hash-text">
                  {truncateHash(file.tx_hash || file.error || '', 10)}
                </span>
                {file.tx_hash && (
                  <button
                    className="copy-btn-small"
                    onClick={() => copyToClipboard(file.tx_hash)}
                    title="Copy TX hash"
                  >
                    📋
                  </button>
                )}
              </td>
              <td>
                <button
                  className="expand-btn"
                  onClick={() => toggleExpand(index)}
                  title="Show details"
                >
                  {expandedRows.has(index) ? '▼' : '▶'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {expandedRows.size > 0 && (
        <div className="expanded-details">
          {Array.from(expandedRows).map((index) => {
            const file = files[index];
            return (
              <div key={index} className="detail-card">
                <h4>{file.filename}</h4>
                <div className="detail-item">
                  <label>Full Hash:</label>
                  <p className="mono">{file.hash || 'N/A'}</p>
                </div>
                {file.recordId && (
                  <div className="detail-item">
                    <label>Record ID:</label>
                    <p className="mono">{file.recordId}</p>
                  </div>
                )}
                {file.tx_hash && (
                  <div className="detail-item">
                    <label>Transaction Hash:</label>
                    <p className="mono">{file.tx_hash}</p>
                  </div>
                )}
                {file.error && (
                  <div className="detail-item error">
                    <label>Error:</label>
                    <p className="mono">{file.error}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default UploadTable;
