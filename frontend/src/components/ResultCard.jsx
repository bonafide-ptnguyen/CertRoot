import { useState } from 'react';
import '../styles/result-card.css';

const ResultCard = ({ result, onClose }) => {
  const [copied, setCopied] = useState({ hash: false, recordId: false, txHash: false });

  const handleCopy = (text, field) => {
    navigator.clipboard.writeText(text);
    setCopied({ ...copied, [field]: true });
    setTimeout(() => {
      setCopied({ ...copied, [field]: false });
    }, 2000);
  };

  const isOriginal = result.status === 'original';

  return (
    <div className="result-card-overlay">
      {/* Backdrop */}
      <div className="result-backdrop" onClick={onClose}></div>

      {/* Modal Card */}
      <div className={`result-card-modal ${isOriginal ? 'original' : 'no-match'}`}>
        {/* Close Button */}
        <button className="result-close-btn" onClick={onClose} title="Close">
          ✕
        </button>

        {/* Header */}
        <div className="result-header">
          <div className="result-status">
            {isOriginal ? (
              <>
                <span className="status-icon">✅</span>
                <div className="status-text">
                  <h2>Original File</h2>
                  <p>File verified successfully</p>
                </div>
              </>
            ) : (
              <>
                <span className="status-icon">❓</span>
                <div className="status-text">
                  <h2>No Match Found</h2>
                  <p>File not registered in system</p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Divider */}
        <div className="result-divider"></div>

        {/* Content */}
        <div className="result-content">
          {isOriginal ? (
            <>
              {/* Matched File */}
              <div className="result-field">
                <div className="field-label">
                  <span className="label-icon">📄</span>
                  <label>Matched File</label>
                </div>
                <div className="field-value-box">
                  <p className="field-value">{result.matched_file}</p>
                </div>
              </div>

              {/* File Hash */}
              <div className="result-field">
                <div className="field-label">
                  <span className="label-icon">🔐</span>
                  <label>File Hash</label>
                </div>
                <div className="copy-field">
                  <p className="field-value mono">{result.hash}</p>
                  <button
                    className={`copy-btn ${copied.hash ? 'copied' : ''}`}
                    onClick={() => handleCopy(result.hash, 'hash')}
                    title="Copy hash to clipboard"
                  >
                    {copied.hash ? '✓ Copied' : '📋 Copy'}
                  </button>
                </div>
              </div>

              {/* Record ID */}
              <div className="result-field">
                <div className="field-label">
                  <span className="label-icon">🆔</span>
                  <label>Record ID</label>
                </div>
                <div className="copy-field">
                  <p className="field-value">{result.recordId}</p>
                  <button
                    className={`copy-btn ${copied.recordId ? 'copied' : ''}`}
                    onClick={() => handleCopy(result.recordId.toString(), 'recordId')}
                    title="Copy record ID to clipboard"
                  >
                    {copied.recordId ? '✓ Copied' : '📋 Copy'}
                  </button>
                </div>
              </div>

              {/* Block Number */}
              <div className="result-field">
                <div className="field-label">
                  <span className="label-icon">⛓️</span>
                  <label>Block Number</label>
                </div>
                <div className="field-value-box">
                  <p className="field-value">{result.block_num}</p>
                </div>
              </div>

              {/* Timestamp */}
              <div className="result-field">
                <div className="field-label">
                  <span className="label-icon">⏰</span>
                  <label>Timestamp</label>
                </div>
                <div className="field-value-box">
                  <p className="field-value">
                    {new Date(result.timestamp * 1000).toLocaleString()}
                  </p>
                </div>
              </div>

              {/* Hash Verified */}
              <div className="result-field">
                <div className="field-label">
                  <span className="label-icon">✔️</span>
                  <label>Verification Hash</label>
                </div>
                <div className="copy-field">
                  <p className="field-value mono">{result.hash_verified}</p>
                  <button
                    className={`copy-btn ${copied.txHash ? 'copied' : ''}`}
                    onClick={() => handleCopy(result.hash_verified, 'txHash')}
                    title="Copy verification hash to clipboard"
                  >
                    {copied.txHash ? '✓ Copied' : '📋 Copy'}
                  </button>
                </div>
              </div>

              {/* Success Badge */}
              <div className="result-badge success">
                <span>✅ File Verified on Blockchain</span>
              </div>
            </>
          ) : (
            <>
              {/* Message for No Match */}
              <div className="result-field">
                <div className="field-label">
                  <span className="label-icon">ℹ️</span>
                  <label>Status</label>
                </div>
                <div className="field-value-box">
                  <p className="field-value">{result.message}</p>
                </div>
              </div>

              {/* File Hash */}
              <div className="result-field">
                <div className="field-label">
                  <span className="label-icon">🔐</span>
                  <label>File Hash</label>
                </div>
                <div className="copy-field">
                  <p className="field-value mono">{result.hash}</p>
                  <button
                    className={`copy-btn ${copied.hash ? 'copied' : ''}`}
                    onClick={() => handleCopy(result.hash, 'hash')}
                    title="Copy hash to clipboard"
                  >
                    {copied.hash ? '✓ Copied' : '📋 Copy'}
                  </button>
                </div>
              </div>

              {/* Info Box */}
              <div className="no-match-info">
                <p>
                  <strong>ℹ️ This file is not registered in the system.</strong>
                </p>
                <p>
                  This could mean the file is new or has been modified. If you're an admin, you can upload it to register it.
                </p>
              </div>

              {/* Warning Badge */}
              <div className="result-badge warning">
                <span>⚠️ File Not Found in Database</span>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="result-footer">
          <button className="close-button" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultCard;