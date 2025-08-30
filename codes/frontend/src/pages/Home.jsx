// pages/Home.jsx
import { Link } from 'react-router-dom'

const Home = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <section className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          Transform Your Videos into Engaging Teasers
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Our AI-powered platform automatically creates compelling video teasers 
          for educational content or cinematic experiences. Just provide your video, 
          and we'll handle the rest.
        </p>
      </section>

      <section className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        <Link 
          to="/learning" 
          className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow"
        >
          <div className="text-center">
            <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0l-9 5m9-5v6" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">Learning Teasers</h2>
            <p className="text-gray-600">
              Perfect for educational content, courses, and tutorials. Highlights key concepts and summaries.
            </p>
          </div>
        </Link>

        <Link 
          to="/cinematic" 
          className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow"
        >
          <div className="text-center">
            <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">Cinematic Teasers</h2>
            <p className="text-gray-600">
              Ideal for films, documentaries, and visual stories. Captures the most compelling visual moments.
            </p>
          </div>
        </Link>
      </section>

      <section className="mt-16 text-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-blue-600 font-bold text-2xl mb-2">1</div>
            <h3 className="font-semibold mb-2">Upload Your Video</h3>
            <p className="text-gray-600">Provide a YouTube URL or upload your video file</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-blue-600 font-bold text-2xl mb-2">2</div>
            <h3 className="font-semibold mb-2">AI Processing</h3>
            <p className="text-gray-600">Our AI analyzes content and extracts the best moments</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-blue-600 font-bold text-2xl mb-2">3</div>
            <h3 className="font-semibold mb-2">Download Teaser</h3>
            <p className="text-gray-600">Receive your professionally crafted video teaser</p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Home