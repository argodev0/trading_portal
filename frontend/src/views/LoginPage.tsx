import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Alert, Paper } from '@mui/material';
import axios from 'axios';
import { environment } from '../config/environment';

interface LoginPageProps {
  onLoginSuccess?: () => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const response = await axios.post('/api/auth/token/', {
        username: email,
        password,
      });
      localStorage.setItem('authToken', response.data.access);
      
      // Call the success callback if provided, otherwise redirect
      if (onLoginSuccess) {
        onLoginSuccess();
      } else {
        window.location.href = '/';
      }
    } catch (err: any) {
      setError('Invalid username or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh" bgcolor="#0F1419">
      <Paper elevation={3} sx={{ p: 4, minWidth: 320, bgcolor: '#1A1F29' }}>
        <Typography variant="h5" mb={2} align="center" color="primary.main">
          Trading Portal Login
        </Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <form onSubmit={handleSubmit}>
          <TextField
            label="Username"
            type="text"
            value={email}
            onChange={e => setEmail(e.target.value)}
            fullWidth
            required
            margin="normal"
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            fullWidth
            required
            margin="normal"
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            disabled={loading}
            sx={{ mt: 2 }}
          >
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>
      </Paper>
    </Box>
  );
};

export default LoginPage;
