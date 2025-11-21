import { useRef } from 'react';
import '../styles/file-upload.css';

const FileUploadArea = ({ onFileSelected, loading, disabled }) => {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      console.log('File selected:', file.name, file.type, file.size);
      onFileSelected(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (disabled) return;

    const file = e.dataTransfer.files[0];
    if (file) {
      console.log('File dropped:', file.name, file.type, file.size);
      onFileSelected(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleClick = () => {
    if (!disabled) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div
      className={`file-upload-area ${loading ? 'uploading' : ''} ${disabled ? 'disabled' : ''}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onClick={handleClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileChange}
        style={{ display: 'none' }}
        disabled={disabled}
      />
      
      <div className="upload-icon">📁</div>
      <h3>Drop your file here</h3>
      <p>or click to browse</p>
      <span className="file-types">Supports all file types</span>
    </div>
  );
};

export default FileUploadArea;