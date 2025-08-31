import { useNavigate } from "react-router-dom";
import { User } from "lucide-react";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-tr from-purple-600 via-pink-500 to-orange-400 text-white text-center p-6 relative">
      {/* Profile Icon - Navigate to Dashboard */}
      <button
        onClick={() => navigate("/profile")}
        className="absolute top-6 right-6 p-2 bg-white text-purple-700 rounded-full shadow-md hover:bg-gray-200 transition"
        title="View Dashboard"
      >
        <User size={28} />
      </button>

      {/* Page Content */}
      <h1 className="text-5xl font-extrabold drop-shadow-lg">Teaser Generator</h1>
      <p className="text-lg mt-4 opacity-90">
        Turn your videos into cinematic teasers instantly!
      </p>
      <div className="flex gap-4 mt-8">
        <a
          href="/learning"
          className="bg-white text-purple-700 px-6 py-3 rounded-full shadow-md hover:shadow-lg hover:bg-gray-200 transition"
        >
          Learning Mode
        </a>
        <a
          href="/cinematic"
          className="bg-purple-700 text-white px-6 py-3 rounded-full shadow-md hover:shadow-lg hover:bg-purple-800 transition"
        >
          Cinematic Mode
        </a>
      </div>
    </div>
  );
}