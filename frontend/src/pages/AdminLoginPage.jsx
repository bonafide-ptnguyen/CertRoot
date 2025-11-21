import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import SpaceBackground from '../components/SpaceBackground';
import '../styles/admin-login.css';

const AdminLoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showRegister, setShowRegister] = useState(false);
  const [registerData, setRegisterData] = useState({
    username: '',
    password: '',
    email: '',
    full_name: ''
  });

  const navigate = useNavigate();
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      console.log('Attempting login...');
      const response = await fetch(`${API_URL}/admin/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      console.log('Login response:', data);

      if (data.status === 'success' && data.access_token) {
        // Store token properly
        localStorage.setItem('admin_token', data.access_token);
        localStorage.setItem('admin_info', JSON.stringify(data.admin));
        console.log('Token stored:', data.access_token);
        
        // Navigate to admin page
        navigate('/admin');
      } else {
        setError(data.detail || data.error || 'Login failed');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        username: registerData.username,
        password: registerData.password,
        email: registerData.email,
        full_name: registerData.full_name
      });

      const response = await fetch(`${API_URL}/admin/register?${params}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (data.status === 'success') {
        setError(null);
        alert('Admin registered successfully! Now login with your credentials.');
        setShowRegister(false);
        setRegisterData({ username: '', password: '', email: '', full_name: '' });
      } else {
        setError(data.detail || data.error || 'Registration failed');
      }
    } catch (err) {
      console.error('Registration error:', err);
      setError('Failed to register');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <SpaceBackground />
      <Header />
      
      <div className="content-wrapper">
        <div className="login-container">
          <div className="login-card">
            <div className="login-header">
              <h1>🔐 Admin Login</h1>
              <p>Access the file management dashboard</p>
            </div>

            {error && (
              <div className="error-banner">
                <p>⚠️ {error}</p>
              </div>
            )}

            {!showRegister ? (
              <form onSubmit={handleLogin} className="login-form">
                <div className="form-group">
                  <label>Username</label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter your username"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Password</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    required
                  />
                </div>

                <button type="submit" className="btn-login" disabled={loading}>
                  {loading ? '🔄 Logging in...' : '🔓 Login'}
                </button>

                <div className="register-link">
                  <p>Don't have an account?</p>
                  <button 
                    type="button"
                    className="btn-register"
                    onClick={() => setShowRegister(true)}
                  >
                    Register as Admin
                  </button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleRegister} className="login-form">
                <div className="form-group">
                  <label>Full Name</label>
                  <input
                    type="text"
                    value={registerData.full_name}
                    onChange={(e) => setRegisterData({...registerData, full_name: e.target.value})}
                    placeholder="Enter full name"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    value={registerData.email}
                    onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                    placeholder="Enter email"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Username</label>
                  <input
                    type="text"
                    value={registerData.username}
                    onChange={(e) => setRegisterData({...registerData, username: e.target.value})}
                    placeholder="Choose a username"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Password</label>
                  <input
                    type="password"
                    value={registerData.password}
                    onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                    placeholder="Create a password"
                    required
                  />
                </div>

                <button type="submit" className="btn-login" disabled={loading}>
                  {loading ? '🔄 Registering...' : '✅ Register'}
                </button>

                <button 
                  type="button"
                  className="btn-back"
                  onClick={() => setShowRegister(false)}
                >
                  ← Back to Login
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminLoginPage;