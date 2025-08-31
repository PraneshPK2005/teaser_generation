// pages/Result.jsx
import { useState, useEffect } from "react";
import { useLocation, Link } from "react-router-dom";
import { ArrowLeft, Download, Home } from "lucide-react";

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
      <div className="flex flex-col items-center justify-center h-screen text-white bg-gradient-to-br from-purple-800 via-pink-600 to-orange-500">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mb-4"></div>
        <p className="text-lg font-medium">Loading your results...</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-100 text-center p-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-3">No Results Found</h2>
        <p className="text-gray-600 mb-6">
          It seems there was an issue generating your teaser. Please try again.
        </p>
        <Link
          to="/"
          className="flex items-center px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition"
        >
          <Home className="w-5 h-5 mr-2" /> Go Back Home
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black text-white p-6">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Title */}
        <header className="text-center space-y-3">
          <h1 className="text-4xl md:text-5xl font-extrabold drop-shadow-lg">
            Your Teaser is Ready!
          </h1>
          <p className="text-lg text-gray-300">
            Duration: <span className="font-semibold">{result.duration}s</span>
          </p>
        </header>

        {/* Video Preview Card */}
        <div className="bg-gray-800 rounded-2xl shadow-lg p-5 space-y-6">
          <video
            controls
            src={result.s3_url}
            poster={result.thumbnail_url || ""}
            className="rounded-xl w-full shadow-md"
          >
            Your browser does not support the video tag.
          </video>

          <div className="flex gap-4">
            <a
              href={result.s3_url}
              download
              className="flex items-center justify-center flex-1 px-5 py-3 bg-purple-600 rounded-xl hover:bg-purple-700 transition font-medium shadow-md"
            >
              <Download className="w-5 h-5 mr-2" /> Download Teaser
            </a>
            <Link
              to="/"
              className="flex items-center justify-center flex-1 px-5 py-3 bg-gray-700 rounded-xl hover:bg-gray-600 transition font-medium shadow-md"
            >
              <ArrowLeft className="w-5 h-5 mr-2" /> Create Another
            </Link>
          </div>

          {/* Video Details */}
          <div className="bg-gray-700 p-4 rounded-xl mt-4">
            <h3 className="text-xl font-semibold mb-3">Details</h3>
            <div className="space-y-2 text-sm md:text-base">
              <div>
                <span className="font-semibold text-gray-300">Original Video: </span>
                <a
                  href={result.video_s3_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-purple-400 hover:underline break-all"
                >
                  {result.video_s3_url}
                </a>
              </div>
              <div>
                <span className="font-semibold text-gray-300">Audio Source: </span>
                <a
                  href={result.audio_s3_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-purple-400 hover:underline break-all"
                >
                  {result.audio_s3_url}
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Timestamps */}
        {result.timestamps && result.timestamps.length > 0 && (
          <div className="bg-gray-800 rounded-2xl shadow-lg p-5">
            <h3 className="text-2xl font-semibold mb-4">Timestamps Used</h3>
            <ul className="space-y-3 text-gray-300">
              {result.timestamps.map((timestamp, index) => (
                <li
                  key={index}
                  className="flex justify-between bg-gray-700 px-4 py-2 rounded-lg hover:bg-gray-600 transition"
                >
                  <span>
                    {timestamp.start}s - {timestamp.end}s
                  </span>
                  <span className="font-medium">
                    Duration: {timestamp.end - timestamp.start}s
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default Result;
