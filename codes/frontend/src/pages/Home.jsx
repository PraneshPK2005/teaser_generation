// pages/Home.jsx
import { useNavigate } from "react-router-dom";
import { User, Book, Film, Sparkles, Brain, Clock, BarChart3, Server } from "lucide-react";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 text-white p-6">
      {/* Profile Icon */}
      <button
        onClick={() => navigate("/profile")}
        className="absolute top-8 right-8 p-3 bg-purple-700/30 backdrop-blur-md border border-purple-500/30 text-white rounded-xl shadow-lg hover:bg-purple-600/40 transition-all duration-300 z-10"
        title="View Dashboard"
      >
        <User size={28} />
      </button>

      {/* Main Content */}
      <div className="flex flex-col items-center justify-center flex-grow text-center max-w-6xl mx-auto">
        <div className="w-24 h-24 bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-2xl">
          <Film size={48} className="text-white" />
        </div>
        
        <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-white to-purple-300 bg-clip-text text-transparent">
          AI Teaser Generator
        </h1>
        
        <p className="text-xl mb-10 text-purple-200 max-w-2xl mx-auto leading-relaxed">
          Transform your videos into captivating cinematic or educational teasers with our advanced AI-powered platform
        </p>
        
        <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16">
          <button
            onClick={() => navigate("/learning")}
            className="flex items-center justify-center gap-3 bg-blue-700/40 backdrop-blur-md border border-blue-500/30 text-white px-8 py-4 rounded-xl shadow-lg hover:bg-blue-600/50 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5"
          >
            <Book size={24} />
            Learning Mode
          </button>
          
          <button
            onClick={() => navigate("/cinematic")}
            className="flex items-center justify-center gap-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-xl shadow-lg hover:from-purple-700 hover:to-pink-700 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5 font-semibold"
          >
            <Film size={24} />
            Cinematic Mode
          </button>
        </div>

        {/* Features Section */}
        <div className="w-full mt-16">
          <h2 className="text-3xl font-bold mb-12 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
            Powered by Advanced AI Technologies
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-gray-800/40 backdrop-blur-md p-6 rounded-2xl border border-purple-500/20 hover:border-purple-500/40 transition-all">
              <div className="w-14 h-14 bg-purple-700/30 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <Sparkles className="h-7 w-7 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">AI-Powered Analysis</h3>
              <p className="text-gray-300">Whisper transcription and BLIP visual analysis for precise content understanding</p>
            </div>
            
            <div className="bg-gray-800/40 backdrop-blur-md p-6 rounded-2xl border border-blue-500/20 hover:border-blue-500/40 transition-all">
              <div className="w-14 h-14 bg-blue-700/30 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <Brain className="h-7 w-7 text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Smart Processing</h3>
              <p className="text-gray-300">Multiple processing methods tailored for different content types and goals</p>
            </div>
            
            <div className="bg-gray-800/40 backdrop-blur-md p-6 rounded-2xl border border-pink-500/20 hover:border-pink-500/40 transition-all">
              <div className="w-14 h-14 bg-pink-700/30 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <Clock className="h-7 w-7 text-pink-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Time-Efficient</h3>
              <p className="text-gray-300">Generate professional teasers in minutes instead of hours of manual editing</p>
            </div>
            
            <div className="bg-gray-800/40 backdrop-blur-md p-6 rounded-2xl border border-green-500/20 hover:border-green-500/40 transition-all">
              <div className="w-14 h-14 bg-green-700/30 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <Server className="h-7 w-7 text-green-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Cloud Powered</h3>
              <p className="text-gray-300">AWS S3 integration for secure storage and fast processing of your media files</p>
            </div>
          </div>
        </div>

        {/* How It Works Section */}
        <div className="w-full mt-20">
          <h2 className="text-3xl font-bold mb-12 bg-gradient-to-r from-white to-purple-300 bg-clip-text text-transparent">
            How It Works
          </h2>
          
          <div className="flex flex-col md:flex-row justify-between items-start gap-8">
            <div className="flex-1 bg-gray-800/40 backdrop-blur-md p-6 rounded-2xl border border-indigo-500/20">
              <div className="text-4xl font-bold bg-gradient-to-r from-blue-500 to-cyan-500 bg-clip-text text-transparent mb-4">1</div>
              <h3 className="text-xl font-semibold mb-3">Upload Your Content</h3>
              <p className="text-gray-300">Provide a YouTube URL or upload your video file directly to our platform</p>
            </div>
            
            <div className="flex-1 bg-gray-800/40 backdrop-blur-md p-6 rounded-2xl border border-purple-500/20">
              <div className="text-4xl font-bold bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text text-transparent mb-4">2</div>
              <h3 className="text-xl font-semibold mb-3">AI Processing</h3>
              <p className="text-gray-300">Our AI analyzes your content to identify the most compelling moments</p>
            </div>
            
            <div className="flex-1 bg-gray-800/40 backdrop-blur-md p-6 rounded-2xl border border-pink-500/20">
              <div className="text-4xl font-bold bg-gradient-to-r from-pink-500 to-red-500 bg-clip-text text-transparent mb-4">3</div>
              <h3 className="text-xl font-semibold mb-3">Generate & Download</h3>
              <p className="text-gray-300">Receive your professionally crafted teaser ready to download and share</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}