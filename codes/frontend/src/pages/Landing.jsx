// pages/Landing.jsx
import { useNavigate } from 'react-router-dom';
import { PlayCircle, Sparkles, Video, Brain } from 'lucide-react';

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-indigo-900 via-purple-900 to-blue-900 text-white">
      {/* Navbar */}
      <header className="flex items-center justify-between px-8 py-6 bg-black/30 backdrop-blur-md border-b border-indigo-500/30">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
          AI Teaser Generator
        </h1>
        <div className="space-x-4">
          <button
            onClick={() => navigate('/login')}
            className="px-6 py-2.5 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20 font-medium hover:bg-white/20 transition-all duration-300 shadow-lg hover:shadow-xl"
          >
            Log In
          </button>
          <button
            onClick={() => navigate('/signup')}
            className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 font-medium hover:from-indigo-600 hover:to-purple-600 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            Sign Up
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center flex-grow text-center px-6 py-16">
        <div className="mb-8">
          <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-r from-pink-500 to-orange-500 rounded-full flex items-center justify-center shadow-2xl">
            <PlayCircle size={48} className="text-white" />
          </div>
          <h2 className="text-5xl md:text-6xl font-bold leading-tight mb-6 bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent">
            Create Stunning Video Teasers <br /> in Minutes
          </h2>
          <p className="mt-6 text-xl max-w-3xl opacity-90 leading-relaxed">
            Our platform uses <span className="font-semibold text-yellow-300">AI-driven analysis</span> to generate
            cinematic or learning teasers from your raw video content — saving you hours of manual editing.
          </p>
        </div>

        <div className="mt-10 flex gap-6">
          <button
            onClick={() => navigate('/signup')}
            className="px-8 py-4 rounded-xl bg-gradient-to-r from-pink-500 to-orange-500 font-semibold text-lg shadow-2xl hover:shadow-3xl hover:scale-105 transition-all duration-300 flex items-center gap-2"
          >
            <Sparkles size={20} />
            Get Started
          </button>
          <button
            onClick={() => navigate('/login')}
            className="px-8 py-4 rounded-xl border-2 border-white/30 font-semibold text-lg backdrop-blur-sm hover:bg-white/10 transition-all duration-300"
          >
            Log In
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-gradient-to-b from-white to-gray-100 text-gray-800 py-20 px-6 md:px-20">
        <div className="max-w-7xl mx-auto">
          <h3 className="text-4xl font-bold text-center mb-16 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            How Our AI Teaser Generator Works
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 bg-white group hover:-translate-y-2">
              <div className="w-16 h-16 bg-indigo-100 rounded-2xl flex items-center justify-center mb-6 group-hover:bg-indigo-200 transition-colors">
                <Video className="h-8 w-8 text-indigo-600" />
              </div>
              <h4 className="font-bold text-xl mb-4 text-indigo-800">1. Upload Your Video</h4>
              <p className="text-gray-600 leading-relaxed">
                Start by uploading your cinematic or learning content in supported formats like MP4 or WAV.
              </p>
            </div>
            <div className="p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 bg-white group hover:-translate-y-2">
              <div className="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mb-6 group-hover:bg-purple-200 transition-colors">
                <Brain className="h-8 w-8 text-purple-600" />
              </div>
              <h4 className="font-bold text-xl mb-4 text-purple-800">2. AI Analysis</h4>
              <p className="text-gray-600 leading-relaxed">
                Our AI extracts key moments, analyzes timestamps, and processes visuals with context.
              </p>
            </div>
            <div className="p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 bg-white group hover:-translate-y-2">
              <div className="w-16 h-16 bg-pink-100 rounded-2xl flex items-center justify-center mb-6 group-hover:bg-pink-200 transition-colors">
                <Sparkles className="h-8 w-8 text-pink-600" />
              </div>
              <h4 className="font-bold text-xl mb-4 text-pink-800">3. Generate Teaser</h4>
              <p className="text-gray-600 leading-relaxed">
                Get a professionally curated teaser optimized for cinematic appeal or learning clarity.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Footer */}
      <footer className="text-center py-8 bg-black/20 backdrop-blur-md border-t border-indigo-500/20">
        <p className="text-sm opacity-80">
          © {new Date().getFullYear()} AI Teaser Generator. All rights reserved.
        </p>
      </footer>
    </div>
  );
};

export default Landing;