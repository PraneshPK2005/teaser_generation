// pages/Home.jsx
import { useNavigate } from "react-router-dom";
import { User, Book, Film } from "lucide-react";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-tr from-purple-700 via-pink-600 to-orange-500 text-white text-center p-6 relative">
      {/* Profile Icon */}
      <button
        onClick={() => navigate("/profile")}
        className="absolute top-8 right-8 p-3 bg-white/10 backdrop-blur-md border border-white/20 text-white rounded-xl shadow-lg hover:bg-white/20 transition-all duration-300"
        title="View Dashboard"
      >
        <User size={28} />
      </button>

      {/* Page Content */}
      <div className="max-w-2xl mx-auto">
        <div className="w-24 h-24 bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-2xl">
          <Film size={48} className="text-white" />
        </div>
        
        <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent">
          Teaser Generator
        </h1>
        
        <p className="text-xl mb-10 text-white/90 max-w-md mx-auto leading-relaxed">
          Turn your videos into engaging cinematic or educational teasers instantly!
        </p>
        
        <div className="flex flex-col sm:flex-row gap-6 justify-center">
          <button
            onClick={() => navigate("/learning")}
            className="flex items-center justify-center gap-3 bg-white/10 backdrop-blur-md border border-white/20 text-white px-8 py-4 rounded-xl shadow-lg hover:bg-white/20 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5"
          >
            <Book size={24} />
            Learning Mode
          </button>
          
          <button
            onClick={() => navigate("/cinematic")}
            className="flex items-center justify-center gap-3 bg-white text-purple-700 px-8 py-4 rounded-xl shadow-lg hover:bg-gray-100 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5 font-semibold"
          >
            <Film size={24} />
            Cinematic Mode
          </button>
        </div>
      </div>
    </div>
  );
}