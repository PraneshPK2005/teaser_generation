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
      { withCredentials: true } // send session cookie
    )
    alert(res.data.message)
    navigate('/home') // no need to store user in localStorage
  } catch (err) {
    setError(err.response?.data?.detail || 'Login failed')
  }
}

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500">
      <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-lg p-8 w-96 text-white">
        <h2 className="text-2xl font-bold text-center mb-6">Welcome Back</h2>
        {error && <p className="bg-red-500 text-white p-2 rounded mb-3 text-center">{error}</p>}
        <form onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email"
            className="w-full p-3 mb-4 rounded-lg bg-white/20 placeholder-gray-200 focus:outline-none focus:ring-2 focus:ring-pink-400"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full p-3 mb-4 rounded-lg bg-white/20 placeholder-gray-200 focus:outline-none focus:ring-2 focus:ring-pink-400"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button className="w-full bg-pink-500 hover:bg-pink-600 text-white font-semibold p-3 rounded-lg shadow-md transition">
            Login
          </button>
        </form>
        <p className="text-sm text-center mt-4">
          Don’t have an account?{' '}
          <a href="/signup" className="text-yellow-300 hover:underline">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}
