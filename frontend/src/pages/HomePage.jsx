import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import SpaceBackground from '../components/SpaceBackground';
import '../styles/home-page.css';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="page-container">
      <SpaceBackground />
      <Header />
      
      <div className="content-wrapper">
        <div className="home-content">
          <div className="hero-section">
            <h1 className="hero-title">CertRoot</h1>
            {/* <h2 className="hero-title">File Integrity Verification</h2> */}
            <p className="hero-subtitle">
              Verify the authenticity of your files using blockchain technology
            </p>
          </div>

          <div className="modes-container">
            <div className="mode-card user-mode" onClick={() => navigate('/verify')}>
              <div className="mode-icon">👤</div>
              <h2>User Mode</h2>
              <p>Upload and verify a file for integrity</p>
              <button className="mode-btn">Start Verifying</button>
            </div>

            <div className="mode-card admin-mode" onClick={() => navigate('/admin-login')}>
              <div className="mode-icon">👨‍💼</div>
              <h2>Admin Mode</h2>
              <p>Login to access the file management dashboard</p>
              <button className="mode-btn">Admin Login</button>
            </div>
          </div>

          <div className="features-section">
            <h3>Key Features</h3>
            <div className="features-grid">
              <div className="feature">
                <span className="feature-icon">🔒</span>
                <h4>Secure Hashing</h4>
                <p>BLAKE3 cryptographic hashing for absolute file integrity</p>
              </div>
              <div className="feature">
                <span className="feature-icon">⛓️</span>
                <h4>Blockchain Verified</h4>
                <p>All files are stored on blockchain for immutable records</p>
              </div>
              <div className="feature">
                <span className="feature-icon">🔐</span>
                <h4>Secure Login</h4>
                <p>Admin authentication with JWT tokens for security</p>
              </div>
              <div className="feature">
                <span className="feature-icon">📁</span>
                <h4>Any File Type</h4>
                <p>Support for documents, images, 3D models, archives, and more</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
