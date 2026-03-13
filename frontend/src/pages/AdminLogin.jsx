import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Configure axios to send credentials
axios.defaults.withCredentials = true;

export default function AdminLogin() {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post(
        `${API_URL}/api/admin/login`,
        credentials,
        { withCredentials: true } // Important: send cookies
      );

      if (response.data.success) {
        // Store admin info in localStorage as backup
        localStorage.setItem('admin', JSON.stringify(response.data.admin));
        
        // Navigate to dashboard
        navigate('/admin/dashboard');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err.response?.data?.error || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1f2937 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        borderRadius: '20px',
        padding: '40px',
        maxWidth: '450px',
        width: '100%',
        boxShadow: '0 25px 50px rgba(0, 0, 0, 0.5)',
        border: '1px solid rgba(255, 255, 255, 0.2)'
      }}>
        {/* Lock Icon */}
        <div style={{
          textAlign: 'center',
          marginBottom: '30px',
          animation: 'bounce 2s infinite'
        }}>
          <div style={{ fontSize: '60px' }}>🔐</div>
        </div>

        {/* Title */}
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h1 style={{ fontSize: '36px', color: 'white', marginBottom: '10px' }}>
            Fixxo Admin
          </h1>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
            Hostel Management Dashboard
          </p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          {/* Username */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              fontWeight: 'bold',
              marginBottom: '8px',
              color: 'white'
            }}>
              Username
            </label>
            <div style={{ position: 'relative' }}>
              <span style={{
                position: 'absolute',
                left: '15px',
                top: '50%',
                transform: 'translateY(-50%)',
                fontSize: '20px'
              }}>
                👤
              </span>
              <input
                type="text"
                required
                value={credentials.username}
                onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                style={{
                  width: '100%',
                  padding: '12px 12px 12px 45px',
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '10px',
                  fontSize: '16px',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                  outline: 'none'
                }}
                placeholder="Enter username"
              />
            </div>
          </div>

          {/* Password */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              fontWeight: 'bold',
              marginBottom: '8px',
              color: 'white'
            }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <span style={{
                position: 'absolute',
                left: '15px',
                top: '50%',
                transform: 'translateY(-50%)',
                fontSize: '20px'
              }}>
                🔑
              </span>
              <input
                type="password"
                required
                value={credentials.password}
                onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                style={{
                  width: '100%',
                  padding: '12px 12px 12px 45px',
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '10px',
                  fontSize: '16px',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                  outline: 'none'
                }}
                placeholder="Enter password"
              />
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div style={{
              backgroundColor: 'rgba(239, 68, 68, 0.2)',
              border: '2px solid #ef4444',
              borderRadius: '10px',
              padding: '15px',
              marginBottom: '20px',
              color: '#fecaca',
              animation: 'shake 0.5s'
            }}>
              ❌ {error}
            </div>
          )}

          {/* Login Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              background: 'linear-gradient(135deg, #a78bfa 0%, #60a5fa 100%)',
              color: 'white',
              fontWeight: 'bold',
              padding: '15px',
              borderRadius: '10px',
              border: 'none',
              fontSize: '18px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1,
              marginBottom: '20px'
            }}
          >
            {loading ? 'Logging in...' : 'Login to Dashboard'}
          </button>

          {/* Default Credentials Hint */}
          <div style={{
            textAlign: 'center',
            padding: '15px',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '10px',
            color: 'rgba(255, 255, 255, 0.6)',
            fontSize: '14px'
          }}>
            <p style={{ margin: '5px 0' }}>Default Credentials:</p>
            <p style={{ margin: '5px 0' }}>Username: <strong style={{ color: 'white' }}>admin</strong></p>
            <p style={{ margin: '5px 0' }}>Password: <strong style={{ color: 'white' }}>admin123</strong></p>
          </div>
        </form>

        {/* Footer */}
        <div style={{
          textAlign: 'center',
          marginTop: '30px',
          color: 'rgba(255, 255, 255, 0.5)',
          fontSize: '14px'
        }}>
          Powered by Fixxo • Open Source
        </div>
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-10px); }
          75% { transform: translateX(10px); }
        }
      `}</style>
    </div>
  );
}