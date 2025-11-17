import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import SpaceBackground from '../components/SpaceBackground';
import UploadTable from '../components/UploadTable';
import '../styles/admin-page.css';

const AdminPage = () => {
  const [files, setFiles] = useState([]);
  const [stats, setStats] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [adminInfo, setAdminInfo] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const navigate = useNavigate();
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('admin_token');
      const info = localStorage.getItem('admin_info');

      if (!token) {
        navigate('/admin-login');
        return;
      }

      if (info) setAdminInfo(JSON.parse(info));

      await verifyToken(token);
      await fetchStats(token);
    };

    checkAuth();
  }, [navigate]);

  const verifyToken = async (token) => {
    try {
      const response = await fetch(`${API_URL}/admin/verify-token`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_info');
        navigate('/admin-login');
        return false;
      }
      return true;
    } catch (err) {
      console.error('Token verification error:', err);
      navigate('/admin-login');
      return false;
    }
  };

  const fetchStats = async (token) => {
    try {
      const response = await fetch(`${API_URL}/admin/stats`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) throw new Error('Failed to fetch stats');

      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const handleFilesSelected = async (selectedFiles) => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setError(null);

    // Create new files with processing status
    const newFiles = selectedFiles.map((file) => ({
      filename: file.name,
      hash: '',
      recordId: '',
      tx_hash: '',
      status: 'processing',
      error: null
    }));

    setFiles((prev) => [...prev, ...newFiles]);

    try {
      const token = localStorage.getItem('admin_token');
      if (!token) {
        setError('No authentication token found');
        setFiles((prev) =>
          prev.map((pf) => ({
            ...pf,
            status: 'error',
            error: 'No authentication token'
          }))
        );
        setUploading(false);
        return;
      }

      // Create FormData with all files
      const formData = new FormData();
      selectedFiles.forEach((file) => {
        formData.append('files', file);
      });

      console.log(`Uploading ${selectedFiles.length} files...`);

      const response = await fetch(`${API_URL}/admin/upload`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
          // Don't set Content-Type - browser will set it automatically with boundary
        },
        body: formData
      });

      console.log('Upload response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Upload error:', errorText);
        throw new Error(`Upload failed: ${response.status}`);
      }

      const data = await response.json();
      console.log('Upload successful:', data);

      // Update files with response data
      const uploadedFiles = data.uploaded_files || [];
      setFiles((prev) =>
        prev.map((pf) => {
          const uploaded = uploadedFiles.find((uf) => uf.filename === pf.filename);
          if (uploaded) {
            return {
              ...pf,
              hash: uploaded.hash || '',
              recordId: uploaded.recordId || '',
              tx_hash: uploaded.tx_hash || '',
              status: uploaded.status || 'unknown',
              error: uploaded.error || null
            };
          }
          return pf;
        })
      );

      // Show success message
      if (data.cleanup_status === 'completed') {
        alert(
          `✅ Upload Complete!\n\n` +
          `📁 ${data.successful} file(s) verified and processed\n` +
          `🗑️ Files folder cleaned successfully`
        );
      } else if (data.failed > 0) {
        alert(
          `⚠️ Upload Partially Complete\n\n` +
          `✅ Success: ${data.successful}\n` +
          `❌ Failed: ${data.failed}\n\n` +
          `Check the table below for details`
        );
      }

      // Refresh stats
      const token_val = localStorage.getItem('admin_token');
      if (token_val) {
        await fetchStats(token_val);
      }
    } catch (err) {
      console.error('Upload error:', err);
      const errorMsg = err.message || 'Upload failed';
      setError(errorMsg);

      // Mark all files as error
      setFiles((prev) =>
        prev.map((pf) => ({
          ...pf,
          status: 'error',
          error: errorMsg
        }))
      );
    } finally {
      setUploading(false);
    }
  };

  const handleClearUploads = () => {
    if (confirm('Clear all uploaded files from the list?')) {
      setFiles([]);
      setError(null);
    }
  };

  const handleDragDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();

    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0 && !uploading) {
      handleFilesSelected(Array.from(droppedFiles));
    }
  };

  return (
    <div className="page-container">
      <SpaceBackground />
      <Header />

      <div className="content-wrapper">
        <div className="admin-container">
          {/* Page Header */}
          <div className="page-header">
            <div className="header-content">
              <h1> Admin Dashboard</h1>
              <p>Welcome back, {adminInfo?.full_name || 'Admin'}!</p>
            </div>
          </div>

          {/* Stats Cards */}
          {stats && (
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-label">Total Records</span>
                <span className="stat-value">{stats.total_records || 0}</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">CSV Entries</span>
                <span className="stat-value">{stats.csv_entries || 0}</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Files Verified</span>
                <span className="stat-value">
                  {files.filter((f) => f.status === 'success').length}
                </span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Admin</span>
                <span className="stat-value mono">{adminInfo?.username || 'User'}</span>
              </div>
            </div>
          )}

          {/* File Drop Zone */}
          <div
            className="file-drop-zone-modern"
            onDragOver={(e) => e.preventDefault()}
            onDragEnter={(e) => e.preventDefault()}
            onDrop={handleDragDrop}
            onClick={() => !uploading && fileInputRef.current?.click()}
            style={{ cursor: uploading ? 'not-allowed' : 'pointer', opacity: uploading ? 0.7 : 1 }}
          >
            <div className="drop-inner">
              <img
                src="https://cdn-icons-png.flaticon.com/512/716/716784.png"
                alt="folder"
                className="drop-folder-icon"
              />
              <h2 className="drop-title">Drag & Drop Your Files Here</h2>
              <p className="drop-subtext">or click to select files</p>
              <span className="file-types-hint">Supports: Documents, Images, 3D Models, Archives, etc.</span>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={(e) => handleFilesSelected(Array.from(e.target.files || []))}
              style={{ display: 'none' }}
              disabled={uploading}
            />
          </div>

          {/* Upload Progress Indicator */}
          {uploading && (
            <div className="upload-progress">
              <div className="spinner"></div>
              <p>Processing and verifying files...</p>
              <span className="progress-subtext">Please wait, this may take a moment</span>
            </div>
          )}

          {/* Error Banner */}
          {error && (
            <div className="error-banner">
              <span className="error-icon">⚠️</span>
              <p>{error}</p>
              <button
                className="error-close"
                onClick={() => setError(null)}
              >
                ✕
              </button>
            </div>
          )}

          {/* Upload Results Table */}
          {files.length > 0 && (
            <div className="upload-results">
              <div className="results-header">
                <h3>
                  📋 Uploaded Files
                  <span className="file-count">
                    ({files.filter((f) => f.status === 'success').length} success / {files.length} total)
                  </span>
                </h3>
                <button className="clear-btn" onClick={handleClearUploads} title="Clear all uploads">
                  🗑️ Clear All
                </button>
              </div>
              <UploadTable files={files} />
            </div>
          )}

          {/* Empty State Message */}
          {files.length === 0 && !uploading && (
            <div className="empty-state">
              <p>📁 No files uploaded yet</p>
              <span>Drop files above to get started</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPage;