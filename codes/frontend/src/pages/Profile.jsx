import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Video, Download, Calendar, Clock, FileText, User, History, BarChart3 } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const Dashboard = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('all');
  const [userStats, setUserStats] = useState({
    totalTeasers: 0,
    learningCount: 0,
    cinematicCount: 0
  });
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.post(`${API_BASE_URL}/profile`, {
          withCredentials: true,
        });

        const sortedHistory = response.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setHistory(sortedHistory);
        
        // Calculate user statistics
        const learningCount = sortedHistory.filter(item => 
          item.method.includes('learning')).length;
        const cinematicCount = sortedHistory.filter(item => 
          item.method.includes('cinematic') || item.method === 'gemini').length;
        
        setUserStats({
          totalTeasers: sortedHistory.length,
          learningCount,
          cinematicCount
        });
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
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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

  const getMethodColor = (method) => {
    const colorMap = {
      'learning_a': 'from-blue-500 to-cyan-500',
      'learning_b': 'from-indigo-500 to-blue-500',
      'cinematic_a': 'from-purple-500 to-pink-500',
      'gemini': 'from-orange-500 to-red-500'
    };
    return colorMap[method] || 'from-gray-500 to-gray-600';
  };

  const filteredHistory = activeTab === 'all' 
    ? history 
    : history.filter(item => 
        activeTab === 'learning' ? item.method.includes('learning') : 
        (item.method.includes('cinematic') || item.method === 'gemini')
      );

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 text-white relative overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1518837695005-2083093ee35b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80')] bg-cover bg-center opacity-20"></div>
        
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent mb-6 relative z-10"></div>
        <p className="text-xl font-medium relative z-10">Loading your history...</p>
        <p className="text-gray-400 mt-2 relative z-10">Please wait while we fetch your data</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 text-white p-6 text-center relative overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1518837695005-2083093ee35b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80')] bg-cover bg-center opacity-20"></div>
        
        <div className="bg-red-500/20 backdrop-blur-sm p-6 rounded-2xl border border-red-500/30 mb-8 relative z-10">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-red-400 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-3xl font-bold mb-4 relative z-10">Error Loading History</h2>
        <p className="text-gray-300 mb-8 max-w-md relative z-10">{error}</p>
        <button
          onClick={() => navigate('/home')}
          className="flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl relative z-10"
        >
          <ArrowLeft className="w-5 h-5 mr-2" /> Go Back Home
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 text-white p-6 relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1518837695005-2083093ee35b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80')] bg-cover bg-center opacity-20"></div>
      
      <div className="max-w-6xl mx-auto relative z-10">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 p-6 bg-gray-800/30 backdrop-blur-md rounded-2xl border border-purple-500/20">
          <div className="flex items-center mb-4 md:mb-0">
            <button
              onClick={() => navigate('/home')}
              className="mr-4 p-3 bg-gray-800/50 backdrop-blur-sm rounded-xl hover:bg-gray-700/50 transition-all border border-gray-700/30"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">
                Your Teaser Dashboard
              </h1>
              <p className="text-gray-300 mt-1">Manage and view your generated teasers</p>
            </div>
          </div>
          <div className="bg-purple-600/20 backdrop-blur-sm px-4 py-2 rounded-xl border border-purple-500/30">
            <span className="font-semibold">{history.length}</span> generated teasers
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-800/30 backdrop-blur-md rounded-2xl p-6 border border-blue-500/20">
            <div className="flex items-center">
              <div className="p-3 bg-blue-500/20 rounded-xl mr-4">
                <BarChart3 className="w-8 h-8 text-blue-400" />
              </div>
              <div>
                <h3 className="text-2xl font-bold">{userStats.totalTeasers}</h3>
                <p className="text-gray-400">Total Teasers</p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-800/30 backdrop-blur-md rounded-2xl p-6 border border-indigo-500/20">
            <div className="flex items-center">
              <div className="p-3 bg-indigo-500/20 rounded-xl mr-4">
                <FileText className="w-8 h-8 text-indigo-400" />
              </div>
              <div>
                <h3 className="text-2xl font-bold">{userStats.learningCount}</h3>
                <p className="text-gray-400">Learning Teasers</p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-800/30 backdrop-blur-md rounded-2xl p-6 border border-pink-500/20">
            <div className="flex items-center">
              <div className="p-3 bg-pink-500/20 rounded-xl mr-4">
                <Video className="w-8 h-8 text-pink-400" />
              </div>
              <div>
                <h3 className="text-2xl font-bold">{userStats.cinematicCount}</h3>
                <p className="text-gray-400">Cinematic Teasers</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-2 mb-8 bg-gray-800/30 backdrop-blur-md rounded-xl p-2 border border-gray-700/30 w-fit">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-6 py-2 rounded-lg transition-all ${activeTab === 'all' ? 'bg-purple-600' : 'hover:bg-gray-700/50'}`}
          >
            All Teasers
          </button>
          <button
            onClick={() => setActiveTab('learning')}
            className={`px-6 py-2 rounded-lg transition-all ${activeTab === 'learning' ? 'bg-blue-600' : 'hover:bg-gray-700/50'}`}
          >
            Learning
          </button>
          <button
            onClick={() => setActiveTab('cinematic')}
            className={`px-6 py-2 rounded-lg transition-all ${activeTab === 'cinematic' ? 'bg-pink-600' : 'hover:bg-gray-700/50'}`}
          >
            Cinematic
          </button>
        </div>

        {filteredHistory.length === 0 ? (
          <div className="text-center py-16 bg-gray-800/30 backdrop-blur-md rounded-2xl shadow-lg border border-gray-700/30">
            <Video className="mx-auto h-16 w-16 text-gray-400 mb-4" />
            <h2 className="text-2xl font-semibold mb-2">No teasers found</h2>
            <p className="text-gray-400 mb-6">
              {activeTab !== 'all' 
                ? `You haven't created any ${activeTab} teasers yet` 
                : 'Your generated teasers will appear here'}
            </p>
            <button
              onClick={() => navigate('/home')}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl"
            >
              Create Your First Teaser
            </button>
          </div>
        ) : (
          <div className="grid gap-6">
            {filteredHistory.map((item, index) => (
              <div key={index} className="bg-gray-800/30 backdrop-blur-md rounded-2xl p-6 shadow-lg border border-gray-700/30 hover:border-purple-500/30 transition-all">
                <div className="flex flex-col md:flex-row justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <div className={`p-2 rounded-lg bg-gradient-to-r ${getMethodColor(item.method)} mr-3`}>
                        <FileText className="w-4 h-4 text-white" />
                      </div>
                      <h2 className="text-xl font-semibold">
                        {getMethodDisplayName(item.method)}
                      </h2>
                    </div>
                    <div className="flex flex-wrap items-center mt-3 text-gray-400 text-sm gap-4">
                      <span className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        {formatDate(item.created_at)}
                      </span>
                      <span className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        {Math.round(item.duration)} seconds
                      </span>
                    </div>
                  </div>
                  <span className="bg-gray-700/50 backdrop-blur-sm px-3 py-1 rounded-full text-xs mt-3 md:mt-0">
                    {item.method}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-300 mb-2">Source</h3>
                    <p className="text-sm break-all bg-gray-900/30 p-3 rounded-lg backdrop-blur-sm">
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
                        className="inline-flex items-center bg-gray-900/30 p-3 rounded-lg hover:bg-gray-900/50 transition-all backdrop-blur-sm"
                      >
                        <Download className="w-4 h-4 mr-2 text-purple-400" />
                        <span>Download Teaser</span>
                      </a>
                    ) : (
                      <span className="text-gray-500 bg-gray-900/30 p-3 rounded-lg inline-block backdrop-blur-sm">Not available</span>
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
                          className="bg-gray-700/50 backdrop-blur-sm px-3 py-1 rounded-lg text-xs"
                        >
                          {timestamp[0]}s - {timestamp[1]}s
                        </span>
                      ))}
                      {item.timestamps_used.length > 5 && (
                        <span className="bg-gray-700/50 backdrop-blur-sm px-3 py-1 rounded-lg text-xs">
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