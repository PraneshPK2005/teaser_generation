// pages/Result.jsx
import { useState, useEffect } from "react";
import { useLocation, Link } from "react-router-dom";
import { ArrowLeft, Download, Home, Clock, Film, Music, Sparkles } from "lucide-react";

const Result = () => {
  const location = useLocation();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (location.state?.result) {
      setResult(location.state.result);
      setLoading(false);
    } else {
      setLoading(false);
    }
  }, [location.state]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen text-white bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mb-6"></div>
        <p className="text-xl font-medium">Loading your results...</p>
        <p className="text-purple-300 mt-2">This may take a moment</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 text-center p-6">
        <div className="bg-red-500/20 backdrop-blur-sm p-6 rounded-2xl border border-red-500/30 mb-8">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-red-400 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-3xl font-bold text-white mb-4">No Results Found</h2>
        <p className="text-purple-300 mb-8 max-w-md">
          It seems there was an issue generating your teaser. Please try again.
        </p>
        <Link
          to="/"
          className="flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg hover:shadow-xl"
        >
          <Home className="w-5 h-5 mr-2" /> Go Back Home
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 text-white p-6">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <header className="text-center space-y-4 py-8">
          <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-teal-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <Sparkles className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold drop-shadow-lg bg-gradient-to-r from-white to-teal-200 bg-clip-text text-transparent">
            Your Teaser is Ready!
          </h1>
          <div className="flex items-center justify-center gap-4 text-lg text-purple-300">
            <Clock className="w-5 h-5" />
            <span>Duration: <span className="font-semibold text-white">{result.duration}s</span></span>
          </div>
        </header>

        {/* Video Preview Card */}
        <div className="bg-gray-800/50 backdrop-blur-md rounded-2xl shadow-2xl p-6 space-y-8 border border-purple-500/30">
          <div className="rounded-xl overflow-hidden shadow-2xl bg-black">
            <video
              controls
              src={result.s3_url}
              poster={result.thumbnail_url || ""}
              className="w-full h-auto"
            >
              Your browser does not support the video tag.
            </video>
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <a
              href={result.s3_url}
              download
              className="flex items-center justify-center flex-1 px-6 py-4 bg-gradient-to-r from-green-500 to-teal-500 rounded-xl hover:from-green-600 hover:to-teal-600 transition-all font-semibold shadow-lg hover:shadow-xl"
            >
              <Download className="w-5 h-5 mr-2" /> Download Teaser
            </a>
            <Link
              to="/home"
              className="flex items-center justify-center flex-1 px-6 py-4 bg-gray-700/50 backdrop-blur-sm rounded-xl hover:bg-gray-700 transition-all font-semibold shadow-lg hover:shadow-xl border border-gray-600/30"
            >
              <ArrowLeft className="w-5 h-5 mr-2" /> Create Another
            </Link>
          </div>

          {/* Video Details */}
          <div className="bg-gray-800/30 backdrop-blur-sm p-6 rounded-xl border border-gray-700/30">
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Film className="w-5 h-5 text-purple-400" />
              Video Details
            </h3>
            <div className="space-y-4 text-sm md:text-base">
              <div>
                <span className="font-semibold text-purple-300">Original Video: </span>
                <a
                  href={result.video_s3_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-teal-400 hover:text-teal-300 underline break-all transition-colors"
                >
                  {result.video_s3_url}
                </a>
              </div>
              <div>
                <span className="font-semibold text-purple-300 flex items-center gap-2">
                  <Music className="w-4 h-4" />
                  Audio Source: 
                </span>
                <a
                  href={result.audio_s3_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-teal-400 hover:text-teal-300 underline break-all transition-colors"
                >
                  {result.audio_s3_url}
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Result;
