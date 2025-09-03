// pages/Signup.jsx
import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';

export default function Signup() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await axios.post(`${API_BASE_URL}/signup`, { username, email, password });
      alert('Signup successful! Please login.');
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Signup failed');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-700 via-purple-700 to-pink-600 relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1519751138087-5bf79df62d5b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80')] bg-cover bg-center opacity-20"></div>

      <div className="bg-white/15 backdrop-blur-xl rounded-3xl shadow-2xl p-10 w-full max-w-md border border-white/20 relative z-10">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a5 5 0 015 5v1a2 2 0 01.293 3.707l-.874.874a2 2 0 01-.707.293H6.288a2 2 0 01-.707-.293l-.874-.874A2 2 0 014 8V7a5 5 0 016-5zm0 16a7 7 0 01-7-7h14a7 7 0 01-7 7z" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-white">Create Account</h2>
          <p className="text-white/80 mt-2">Join us to start creating amazing teasers</p>
        </div>

        {error && (
          <div className="bg-red-500/20 backdrop-blur-sm text-red-100 p-3 rounded-xl mb-6 text-center border border-red-500/30">
            {error}
          </div>
        )}

        <form onSubmit={handleSignup} className="space-y-6">
          <div>
            <input
              type="text"
              placeholder="Username"
              className="w-full p-4 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 placeholder-gray-200 text-white focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-transparent transition-all"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div>
            <input
              type="email"
              placeholder="Email"
              className="w-full p-4 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 placeholder-gray-200 text-white focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-transparent transition-all"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <input
              type="password"
              placeholder="Password"
              className="w-full p-4 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 placeholder-gray-200 text-white focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-transparent transition-all"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button className="w-full bg-gradient-to-r from-pink-500 to-orange-500 text-white font-semibold p-4 rounded-xl shadow-lg hover:shadow-xl hover:from-pink-600 hover:to-orange-600 transition-all duration-300 transform hover:-translate-y-0.5">
            Signup
          </button>
        </form>

        <p className="text-sm text-center mt-8 text-white/80">
          Already have an account?{' '}
          <a href="/login" className="text-yellow-300 hover:text-yellow-200 font-semibold transition-colors">
            Login
          </a>
        </p>
      </div>
    </div>
  );
}
