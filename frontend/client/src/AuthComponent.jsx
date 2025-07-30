import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const AuthComponent = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!username.trim() || !password.trim()) {
      setError('Username and password are required');
      setLoading(false);
      return;
    }

    if (!isLogin && !email.trim()) {
      setError('Email is required for registration');
      setLoading(false);
      return;
    }

    try {
      if (isLogin) {
        // Login
        const response = await axios.post(`${API_BASE_URL}/auth/login`, {
          username,
          password
        });
        
        if (response.data.user_id) {
          localStorage.setItem('token', response.data.user_id); // Using user_id as token for now
          localStorage.setItem('username', response.data.username);
          localStorage.setItem('userId', response.data.user_id);
          onLogin(response.data.user_id, response.data.username, response.data.user_id);
        }
      } else {
        // Register
        const response = await axios.post(`${API_BASE_URL}/auth/register`, {
          username,
          email,
          password
        });
        
        if (response.status === 201) {
          setError('');
          setIsLogin(true);
          setPassword('');
          setEmail('');
          alert('Registration successful! Please login now.');
        }
      }
    } catch (error) {
      setError(error.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>{isLogin ? '🔐 Login' : '📝 Register'}</h2>
        <p>{isLogin ? 'Welcome back!' : 'Create your account'}</p>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
              minLength={3}
              required
            />
          </div>
          
          {!isLogin && (
            <div className="form-group">
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                required
              />
            </div>
          )}
          
          <div className="form-group">
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              minLength={6}
              required
            />
          </div>
          
          <button 
            type="submit" 
            disabled={loading}
            className="btn btn-primary auth-btn"
          >
            {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Register')}
          </button>
        </form>
        
        <div className="auth-switch">
          {isLogin ? (
            <p>
              Don't have an account?{' '}
              <button 
                type="button" 
                onClick={() => {setIsLogin(false); setError(''); setPassword(''); setEmail('');}}
                className="link-button"
              >
                Register here
              </button>
            </p>
          ) : (
            <p>
              Already have an account?{' '}
              <button 
                type="button" 
                onClick={() => {setIsLogin(true); setError(''); setPassword(''); setEmail('');}}
                className="link-button"
              >
                Login here
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthComponent;
