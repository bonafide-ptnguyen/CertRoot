import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/header.css';

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isAdmin = !!localStorage.getItem('admin_token');

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_info');
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header className="header">
      <div className="header-container">
        {/* Logo */}
        <div className="logo" onClick={() => navigate('/')}>
          <span className="logo-icon">🔐</span>
          <span className="logo-text">CertRoot</span>
        </div>

        {/* Navigation */}
        <nav className="nav-menu">
          <button
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
            onClick={() => navigate('/')}
          >
            Home
          </button>

          <button
            className={`nav-link ${isActive('/verify') ? 'active' : ''}`}
            onClick={() => navigate('/verify')}
          >
            Verify
          </button>

          {/* Show Admin link only if NOT logged in */}
          {!isAdmin && (
            <button
              className={`nav-link ${isActive('/admin-login') ? 'active' : ''}`}
              onClick={() => navigate('/admin-login')}
            >
              Admin
            </button>
          )}

          {/* Show Logout button only if logged in as admin */}
          {isAdmin && (
            <button
              className="nav-link logout-btn"
              onClick={handleLogout}
            >
              🚪 Logout
            </button>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;


