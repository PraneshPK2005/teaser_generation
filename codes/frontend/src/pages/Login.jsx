// pages/Login.jsx
import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await axios.post(
        'http://localhost:8000/login',
        { email, password },
        { withCredentials: true }
      )
      alert(res.data.message)
      navigate('/home')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-700 via-purple-700 to-pink-600">
      <div className="bg-white/15 backdrop-blur-xl rounded-3xl shadow-2xl p-10 w-full max-w-md border border-white/20">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-white" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-white">Welcome Back</h2>
          <p className="text-white/80 mt-2">Sign in to your account</p>
        </div>
        
        {error && (
          <div className="bg-red-500/20 backdrop-blur-sm text-red-100 p-3 rounded-xl mb-6 text-center border border-red-500/30">
            {error}
          </div>
        )}
        
        <form onSubmit={handleLogin} className="space-y-6">
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
            Login
          </button>
        </form>
        <p className="text-sm text-center mt-8 text-white/80">
          Don't have an account?{' '}
          <a href="/signup" className="text-yellow-300 hover:text-yellow-200 font-semibold transition-colors">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}