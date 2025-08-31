// pages/Landing.jsx
import { useNavigate } from 'react-router-dom';
import { PlayCircle, Sparkles, Video, Brain } from 'lucide-react';

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-indigo-900 via-purple-800 to-blue-700 text-white">
      {/* Navbar */}
      <header className="flex items-center justify-between px-8 py-6 bg-black/20 backdrop-blur-md">
        <h1 className="text-2xl font-extrabold tracking-wide">AI Teaser Generator</h1>
        <div className="space-x-4">
          <button
            onClick={() => navigate('/login')}
            className="px-5 py-2 rounded-full bg-white text-indigo-700 font-medium hover:scale-105 shadow-md transition"
          >
            Log In
          </button>
          <button
            onClick={() => navigate('/signup')}
            className="px-5 py-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 font-medium hover:scale-105 shadow-md transition"
          >
            Sign Up
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center flex-grow text-center px-6 py-12">
        <h2 className="text-5xl md:text-6xl font-extrabold leading-tight drop-shadow-lg">
          Create Stunning Video Teasers <br /> in Minutes
        </h2>
        <p className="mt-6 text-lg md:text-xl max-w-3xl opacity-90">
          Our platform uses <span className="text-yellow-300 font-semibold">AI-driven analysis</span> to generate
          cinematic or learning teasers from your raw video content — saving you hours of manual editing.
        </p>

        <div className="mt-8 flex gap-4">
          <button
            onClick={() => navigate('/signup')}
            className="px-6 py-3 rounded-full bg-gradient-to-r from-pink-500 to-orange-500 font-semibold shadow-lg hover:scale-105 transition"
          >
            Get Started
          </button>
          <button
            onClick={() => navigate('/login')}
            className="px-6 py-3 rounded-full border border-white font-semibold shadow-lg hover:bg-white hover:text-indigo-700 transition"
          >
            Log In
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-white text-gray-800 py-16 px-6 md:px-20">
        <h3 className="text-3xl md:text-4xl font-bold text-center mb-12">
          How Our AI Teaser Generator Works
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 max-w-6xl mx-auto text-center">
          <div className="p-6 rounded-xl shadow-lg hover:shadow-xl transition bg-gray-50">
            <Video className="mx-auto h-12 w-12 text-indigo-600 mb-4" />
            <h4 className="font-semibold text-lg mb-2">1. Upload Your Video</h4>
            <p className="text-gray-600 text-sm">
              Start by uploading your cinematic or learning content in supported formats like MP4 or WAV.
            </p>
          </div>
          <div className="p-6 rounded-xl shadow-lg hover:shadow-xl transition bg-gray-50">
            <Brain className="mx-auto h-12 w-12 text-purple-600 mb-4" />
            <h4 className="font-semibold text-lg mb-2">2. AI Analysis</h4>
            <p className="text-gray-600 text-sm">
              Our AI extracts key moments, analyzes timestamps, and processes visuals with context.
            </p>
          </div>
          <div className="p-6 rounded-xl shadow-lg hover:shadow-xl transition bg-gray-50">
            <Sparkles className="mx-auto h-12 w-12 text-pink-600 mb-4" />
            <h4 className="font-semibold text-lg mb-2">3. Generate Teaser</h4>
            <p className="text-gray-600 text-sm">
              Get a professionally curated teaser optimized for cinematic appeal or learning clarity.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Footer */}
      <footer className="text-center py-6 bg-black/20 backdrop-blur-md">
        <p className="text-sm opacity-80">
          © {new Date().getFullYear()} AI Teaser Generator. All rights reserved.
        </p>
      </footer>
    </div>
  );
};

export default Landing;
