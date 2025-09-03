import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Video, Download, Calendar, Clock, FileText, BarChart3, Filter, Eye, Play, Sparkles, Zap, Cloud, Cpu, Database } from 'lucide-react';
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
    cinematicCount: 0,
    totalDuration: 0
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
        const totalDuration = sortedHistory.reduce((total, item) => total + (item.duration || 0), 0);
        
        setUserStats({
          totalTeasers: sortedHistory.length,
          learningCount,
          cinematicCount,
          totalDuration: Math.round(totalDuration)
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
      'learning_a': 'Learning A',
      'learning_b': 'Learning B',
      'cinematic_a': 'Cinematic A',
      'gemini': 'Gemini AI'
    };
    return methodMap[method] || method;
  };

  const getMethodColor = (method) => {
    const colorMap = {
      'learning_a': 'bg-teal-500/20 text-teal-300 border-teal-500/30',
      'learning_b': 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
      'cinematic_a': 'bg-violet-500/20 text-violet-300 border-violet-500/30',
      'gemini': 'bg-amber-500/20 text-amber-300 border-amber-500/30'
    };
    return colorMap[method] || 'bg-gray-500/20 text-gray-300 border-gray-500/30';
  };

  const getMethodIcon = (method) => {
    if (method.includes('learning')) {
      return <FileText className="w-4 h-4" />;
    } else if (method === 'gemini') {
      return <Cpu className="w-4 h-4" />;
    } else {
      return <Video className="w-4 h-4" />;
    }
  };

  const filteredHistory = activeTab === 'all' 
    ? history 
    : history.filter(item => 
        activeTab === 'learning' ? item.method.includes('learning') : 
        (item.method.includes('cinematic') || item.method === 'gemini')
      );

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 text-white">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-cyan-400 mb-6"></div>
        <p className="text-xl font-medium">Loading your dashboard...</p>
        <p className="text-cyan-300 mt-2">Preparing your analytics</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 text-white p-6 text-center">
        <div className="bg-red-500/20 backdrop-blur-sm p-6 rounded-2xl border border-red-500/30 mb-8">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-red-400 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-3xl font-bold mb-4">Error Loading Dashboard</h2>
        <p className="text-cyan-300 mb-8 max-w-md">{error}</p>
        <button
          onClick={() => navigate('/home')}
          className="flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl hover:from-blue-700 hover:to-cyan-700 transition-all shadow-lg hover:shadow-xl"
        >
          <ArrowLeft className="w-5 h-5 mr-2" /> Go Back Home
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 p-6 bg-slate-800/40 backdrop-blur-xl rounded-2xl border border-cyan-500/20 shadow-2xl">
          <div className="flex items-center mb-4 md:mb-0">
            <button
              onClick={() => navigate('/home')}
              className="mr-4 p-3 bg-cyan-700/30 backdrop-blur-sm rounded-xl hover:bg-cyan-600/40 transition-all border border-cyan-500/30 shadow-lg"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                Creator Studio
              </h1>
              <p className="text-cyan-300 mt-1">Analytics and management for your generated teasers</p>
            </div>
          </div>
          <div className="bg-cyan-600/20 backdrop-blur-sm px-4 py-2 rounded-xl border border-cyan-500/30 flex items-center shadow-lg">
            <Sparkles className="w-5 h-5 mr-2 text-cyan-400" />
            <span className="font-semibold">{history.length}</span> generated teasers
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-slate-800/40 backdrop-blur-md rounded-2xl p-6 border border-cyan-500/30 shadow-lg hover:shadow-xl transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-cyan-500/20 rounded-xl">
                <BarChart3 className="w-6 h-6 text-cyan-400" />
              </div>
              <span className="text-3xl font-bold">{userStats.totalTeasers}</span>
            </div>
            <h3 className="text-lg font-semibold text-cyan-300">Total Teasers</h3>
            <p className="text-blue-300 text-sm">All generated content</p>
          </div>
          
          <div className="bg-slate-800/40 backdrop-blur-md rounded-2xl p-6 border border-teal-500/30 shadow-lg hover:shadow-xl transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-teal-500/20 rounded-xl">
                <FileText className="w-6 h-6 text-teal-400" />
              </div>
              <span className="text-3xl font-bold">{userStats.learningCount}</span>
            </div>
            <h3 className="text-lg font-semibold text-teal-300">Learning</h3>
            <p className="text-blue-300 text-sm">Educational content</p>
          </div>
          
          <div className="bg-slate-800/40 backdrop-blur-md rounded-2xl p-6 border border-violet-500/30 shadow-lg hover:shadow-xl transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-violet-500/20 rounded-xl">
                <Video className="w-6 h-6 text-violet-400" />
              </div>
              <span className="text-3xl font-bold">{userStats.cinematicCount}</span>
            </div>
            <h3 className="text-lg font-semibold text-violet-300">Cinematic</h3>
            <p className="text-blue-300 text-sm">Visual storytelling</p>
          </div>
          
          <div className="bg-slate-800/40 backdrop-blur-md rounded-2xl p-6 border border-blue-500/30 shadow-lg hover:shadow-xl transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-500/20 rounded-xl">
                <Clock className="w-6 h-6 text-blue-400" />
              </div>
              <span className="text-3xl font-bold">{userStats.totalDuration}</span>
            </div>
            <h3 className="text-lg font-semibold text-blue-300">Total Duration</h3>
            <p className="text-blue-300 text-sm">Seconds of content</p>
          </div>
        </div>

        {/* System Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-slate-800/40 backdrop-blur-md rounded-2xl p-5 border border-cyan-500/30 shadow-lg">
            <div className="flex items-center mb-4">
              <div className="p-2 bg-cyan-500/20 rounded-lg mr-3">
                <Zap className="w-5 h-5 text-cyan-400" />
              </div>
              <h3 className="font-semibold">AI Processing</h3>
            </div>
            <p className="text-cyan-300 text-sm">All systems operational</p>
          </div>
          
          <div className="bg-slate-800/40 backdrop-blur-md rounded-2xl p-5 border border-teal-500/30 shadow-lg">
            <div className="flex items-center mb-4">
              <div className="p-2 bg-teal-500/20 rounded-lg mr-3">
                <Cloud className="w-5 h-5 text-teal-400" />
              </div>
              <h3 className="font-semibold">Cloud Storage</h3>
            </div>
            <p className="text-teal-300 text-sm">{(userStats.totalTeasers * 50).toLocaleString()}MB used</p>
          </div>
          
          <div className="bg-slate-800/40 backdrop-blur-md rounded-2xl p-5 border border-violet-500/30 shadow-lg">
            <div className="flex items-center mb-4">
              <div className="p-2 bg-violet-500/20 rounded-lg mr-3">
                <Database className="w-5 h-5 text-violet-400" />
              </div>
              <h3 className="font-semibold">API Requests</h3>
            </div>
            <p className="text-violet-300 text-sm">{userStats.totalTeasers * 3} this month</p>
          </div>
        </div>

        {/* Content Section */}
        <div className="bg-slate-800/40 backdrop-blur-xl rounded-2xl p-6 border border-cyan-500/30 shadow-2xl mb-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold mb-4 md:mb-0 bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              Your Teaser Library
            </h2>
            
            <div className="flex space-x-2 bg-slate-700/50 backdrop-blur-sm rounded-lg p-1 border border-slate-600/30 w-fit shadow-inner">
              <button
                onClick={() => setActiveTab('all')}
                className={`px-4 py-2 rounded-md transition-all flex items-center ${activeTab === 'all' ? 'bg-cyan-600 shadow-md' : 'hover:bg-slate-600/50'}`}
              >
                <Eye className="w-4 h-4 mr-2" /> All
              </button>
              <button
                onClick={() => setActiveTab('learning')}
                className={`px-4 py-2 rounded-md transition-all flex items-center ${activeTab === 'learning' ? 'bg-teal-600 shadow-md' : 'hover:bg-slate-600/50'}`}
              >
                <FileText className="w-4 h-4 mr-2" /> Learning
              </button>
              <button
                onClick={() => setActiveTab('cinematic')}
                className={`px-4 py-2 rounded-md transition-all flex items-center ${activeTab === 'cinematic' ? 'bg-violet-600 shadow-md' : 'hover:bg-slate-600/50'}`}
              >
                <Video className="w-4 h-4 mr-2" /> Cinematic
              </button>
            </div>
          </div>

          {filteredHistory.length === 0 ? (
            <div className="text-center py-16 bg-slate-700/30 rounded-xl border border-slate-600/30">
              <Video className="mx-auto h-16 w-16 text-cyan-400 mb-4" />
              <h2 className="text-2xl font-semibold mb-2">No teasers found</h2>
              <p className="text-cyan-300 mb-6">
                {activeTab !== 'all' 
                  ? `You haven't created any ${activeTab} teasers yet` 
                  : 'Your generated teasers will appear here'}
              </p>
              <button
                onClick={() => navigate('/home')}
                className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 rounded-xl hover:from-cyan-700 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl"
              >
                Create Your First Teaser
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {filteredHistory.map((item, index) => (
                <div key={index} className="bg-slate-700/40 backdrop-blur-lg rounded-xl p-5 border border-slate-600/30 hover:border-cyan-500/30 transition-all group shadow-lg hover:shadow-xl">
                  <div className="flex justify-between items-start mb-4">
                    <div className={`flex items-center ${getMethodColor(item.method)} px-3 py-1 rounded-full text-xs border`}>
                      {getMethodIcon(item.method)}
                      <span className="ml-2">{getMethodDisplayName(item.method)}</span>
                    </div>
                    <span className="text-xs text-cyan-300 bg-cyan-500/10 px-2 py-1 rounded">
                      {Math.round(item.duration)}s
                    </span>
                  </div>
                  
                  <div className="mb-4 relative">
                    <div className="w-full h-40 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 rounded-lg flex items-center justify-center group-hover:from-cyan-600/20 group-hover:to-blue-600/20 transition-all">
                      <div className="w-12 h-12 bg-cyan-600/30 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Play className="w-6 h-6 text-cyan-300 fill-current" />
                      </div>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <h3 className="font-semibold text-lg mb-2 line-clamp-1">{getMethodDisplayName(item.method)} Teaser</h3>
                    <div className="flex items-center text-sm text-cyan-300 mb-2">
                      <Calendar className="w-4 h-4 mr-1" />
                      {formatDate(item.created_at)}
                    </div>
                    <p className="text-sm text-blue-200 line-clamp-2">
                      {item.youtube_url || item.main_file_url || 'Generated teaser'}
                    </p>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    {item.teaser_file_url ? (
                      <a
                        href={item.teaser_file_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 rounded-lg text-sm hover:from-cyan-700 hover:to-blue-700 transition-all shadow-md"
                      >
                        <Download className="w-4 h-4 mr-1" /> Download
                      </a>
                    ) : (
                      <span className="text-xs text-slate-500 bg-slate-800/50 px-3 py-2 rounded-lg">Processing</span>
                    )}
                    
                    <button className="text-cyan-300 hover:text-white transition-colors">
                      <Eye className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="bg-slate-800/40 backdrop-blur-xl rounded-2xl p-6 border border-cyan-500/30 shadow-2xl">
          <h2 className="text-2xl font-semibold mb-6 bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            Recent Activity
          </h2>
          <div className="space-y-4">
            {history.slice(0, 5).map((item, index) => (
              <div key={index} className="flex items-center p-4 bg-slate-700/40 rounded-xl border border-slate-600/30 backdrop-blur-sm">
                <div className={`p-2 rounded-lg ${getMethodColor(item.method)} mr-4`}>
                  {getMethodIcon(item.method)}
                </div>
                <div className="flex-1">
                  <h3 className="font-medium">{getMethodDisplayName(item.method)} Teaser</h3>
                  <p className="text-sm text-cyan-300">{formatDate(item.created_at)}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold">{Math.round(item.duration)}s</p>
                  <p className="text-xs text-cyan-300">Duration</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;