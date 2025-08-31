import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Video, Download, Calendar, Clock, FileText } from 'lucide-react';
import axios from 'axios';

const Dashboard = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        // Fetch user's teaser history from backend using session
        const response = await axios.get('http://localhost:8000/profile', {
          withCredentials: true, // send cookies for session
        });

        const sortedHistory = response.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
setHistory(sortedHistory);
      } catch (err) {
        setError('Failed to fetch history. Please login again.');
        console.error('Error fetching history:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const getMethodDisplayName = (method) => {
    const methodMap = {
      'learning_a': 'Learning Method A',
      'learning_b': 'Learning Method B',
      'cinematic_a': 'Cinematic Method A',
      'gemini': 'Gemini Method'
    };
    return methodMap[method] || method;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen text-white bg-gradient-to-br from-purple-800 via-pink-600 to-orange-500">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mb-4"></div>
        <p className="text-lg font-medium">Loading your history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-100 text-center p-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-3">Error Loading History</h2>
        <p className="text-gray-600 mb-6">{error}</p>
        <button
          onClick={() => navigate('/home')}
          className="flex items-center px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition"
        >
          <ArrowLeft className="w-5 h-5 mr-2" /> Go Back Home
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black text-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <button
              onClick={() => navigate('/home')}
              className="mr-4 p-2 bg-gray-800 rounded-full hover:bg-gray-700 transition"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <h1 className="text-3xl font-bold">Your Teaser History</h1>
          </div>
          <span className="bg-purple-600 px-4 py-2 rounded-full text-sm">
            {history.length} generated teasers
          </span>
        </div>

        {history.length === 0 ? (
          <div className="text-center py-16 bg-gray-800 rounded-2xl shadow-lg">
            <Video className="mx-auto h-16 w-16 text-gray-400 mb-4" />
            <h2 className="text-2xl font-semibold mb-2">No teasers yet</h2>
            <p className="text-gray-400 mb-6">Your generated teasers will appear here</p>
            <button
              onClick={() => navigate('/home')}
              className="px-6 py-3 bg-purple-600 rounded-xl hover:bg-purple-700 transition"
            >
              Create Your First Teaser
            </button>
          </div>
        ) : (
          <div className="grid gap-6">
            {history.map((item, index) => (
              <div key={index} className="bg-gray-800 rounded-2xl p-6 shadow-lg">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-xl font-semibold flex items-center">
                      <FileText className="w-5 h-5 mr-2 text-purple-400" />
                      {getMethodDisplayName(item.method)}
                    </h2>
                    <div className="flex items-center mt-2 text-gray-400 text-sm">
                      <Calendar className="w-4 h-4 mr-1" />
                      <span>{formatDate(item.created_at)}</span>
                      <Clock className="w-4 h-4 ml-4 mr-1" />
                      <span>{Math.round(item.duration)} seconds</span>
                    </div>
                  </div>
                  <span className="bg-gray-700 px-3 py-1 rounded-full text-xs">
                    {item.method}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-300 mb-2">Source</h3>
                    <p className="text-sm break-all">
                      {item.youtube_url || item.main_file_url || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-300 mb-2">Teaser</h3>
                    {item.teaser_file_url ? (
                      <a
                        href={item.teaser_file_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-purple-400 hover:text-purple-300 transition"
                      >
                        <Download className="w-4 h-4 mr-1" />
                        Download Teaser
                      </a>
                    ) : (
                      <span className="text-gray-500">Not available</span>
                    )}
                  </div>
                </div>

                {item.timestamps_used && item.timestamps_used.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-300 mb-2">Timestamps Used</h3>
                    <div className="flex flex-wrap gap-2">
                      {item.timestamps_used.slice(0, 5).map((timestamp, idx) => (
                        <span
                          key={idx}
                          className="bg-gray-700 px-2 py-1 rounded text-xs"
                        >
                          {timestamp[0]}s - {timestamp[1]}s
                        </span>
                      ))}
                      {item.timestamps_used.length > 5 && (
                        <span className="bg-gray-700 px-2 py-1 rounded text-xs">
                          +{item.timestamps_used.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
