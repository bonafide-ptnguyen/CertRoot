import { useState } from 'react';
import Header from '../components/Header';
import SpaceBackground from '../components/SpaceBackground';
import FileUploadArea from '../components/FileUploadArea';
import ResultCard from '../components/ResultCard';
import '../styles/verify-page.css';

const VerifyPage = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleFileSelected = async (selectedFile) => {
    if (!selectedFile) return;

    setFile(selectedFile);
    setResult(null);
    setError(null);
    setLoading(true);

    try {
      console.log('Verifying file:', selectedFile.name);
      
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(`${API_URL}/verify`, {
        method: 'POST',
        body: formData,
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`Verification failed: ${response.status}`);
      }

      const data = await response.json();
      console.log('Verification result:', data);
      setResult(data);
    } catch (err) {
      console.error('Verification error:', err);
      setError(err.message || 'Failed to verify file');
    } finally {
      setLoading(false);
    }
  };

  const handleClearResult = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="page-container">
      <SpaceBackground />
      <Header />
      
      <div className="content-wrapper">
        <div className="verify-container">
          {/* Page Header */}
          <div className="page-header">
            <h1> Verify Your File Integrity</h1>
            <p>Upload a file to check its authenticity and integrity on the blockchain</p>
          </div>

          {/* File Upload Area */}
          <FileUploadArea
            onFileSelected={handleFileSelected}
            loading={loading}
            disabled={loading}
          />

          {/* Loading Indicator */}
          {loading && (
            <div className="loading-container">
              <div className="loading-spinner">
                <div className="spinner"></div>
              </div>
              <h3>Verifying Your File</h3>
              <p>Processing your file... This may take a moment</p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="error-message-card">
              <span className="error-icon">⚠️</span>
              <div className="error-content">
                <h3>Verification Failed</h3>
                <p>{error}</p>
              </div>
              <button
                className="error-close"
                onClick={() => setError(null)}
                title="Close error"
              >
                ✕
              </button>
            </div>
          )}

          {/* Result Modal */}
          {result && (
            <ResultCard result={result} onClose={handleClearResult} />
          )}

          {/* Empty State */}
          {!loading && !result && !error && (
            <div className="verify-info-box">
              <div className="info-content">
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VerifyPage;