// pages/Cinematic.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import VideoInput from '../components/VideoInput'
import { API_BASE_URL } from '../config';

const Cinematic = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    source: 'youtube',
    youtubeUrl: '',
    videoFile: null,
    maxLength: 70,
    minLength: 60,
    method: 'cinematic_a'
  })
  const [isProcessing, setIsProcessing] = useState(false)

  const handleInputChange = (e) => {
    const { name, value, files } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: files ? files[0] : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsProcessing(true)

    try {
      const submitData = new FormData()
      submitData.append('method', formData.method)
      submitData.append('max_length', formData.maxLength)
      submitData.append('min_length', formData.minLength)

      if (formData.source === 'youtube') {
        submitData.append('youtube_url', formData.youtubeUrl)
      } else {
        submitData.append('video_file', formData.videoFile)
      }

      const response = await fetch(`${API_BASE_URL}/generate-teaser`, {
        method: 'POST',
        body: submitData,
        credentials: 'include',
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to generate teaser')
      }

      const result = await response.json()
      navigate('/result', { state: { result } })
    } catch (error) {
      console.error('Error generating teaser:', error)
      alert(`Failed to generate teaser: ${error.message}`)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 py-12 px-6 flex flex-col items-center text-white">
      <div className="text-center mb-10">
        <div className="w-20 h-20 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
          </svg>
        </div>
        <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-white to-purple-300 bg-clip-text text-transparent">
          Cinematic Teaser Generator
        </h1>
        <p className="text-lg text-purple-200 max-w-2xl">
          Capture the most visually compelling moments to create dramatic previews
        </p>
      </div>

      <div className="w-full max-w-3xl bg-gray-800/50 backdrop-blur-md border border-purple-500/30 shadow-2xl rounded-2xl p-8 mb-12">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Video Input */}
          <VideoInput formData={formData} handleInputChange={handleInputChange} />

          {/* Length Controls */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <label className="block text-sm font-semibold mb-3 uppercase tracking-wide text-purple-200">
                Maximum Length (seconds)
              </label>
              <input
                type="number"
                name="maxLength"
                value={formData.maxLength}
                onChange={handleInputChange}
                className="w-full border-2 border-gray-700 rounded-xl px-4 py-3 bg-gray-900/70 text-white focus:outline-none focus:border-purple-500 transition-colors backdrop-blur-sm"
                min="10"
                max="300"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-3 uppercase tracking-wide text-purple-200">
                Minimum Length (seconds)
              </label>
              <input
                type="number"
                name="minLength"
                value={formData.minLength}
                onChange={handleInputChange}
                className="w-full border-2 border-gray-700 rounded-xl px-4 py-3 bg-gray-900/70 text-white focus:outline-none focus:border-purple-500 transition-colors backdrop-blur-sm"
                min="5"
                max="120"
              />
            </div>
          </div>

          {/* Method Selection */}
          <div>
            <label className="block text-sm font-semibold mb-3 uppercase tracking-wide text-purple-200">
              Processing Method
            </label>
            <select
              name="method"
              value={formData.method}
              onChange={handleInputChange}
              className="w-full border-2 border-gray-700 rounded-xl px-4 py-3 bg-gray-900/70 text-white focus:outline-none focus:border-purple-500 transition-colors appearance-none bg-arrow-down bg-no-repeat bg-right-4 bg-[length:20px] backdrop-blur-sm"
              style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23D8B4FE'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E\")" }}
            >
              <option value="cinematic_a">Cinematic Method A (Visual Appeal)</option>
              <option value="gemini">Gemini Method (Balanced Approach)</option>
            </select>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isProcessing}
            className={`w-full py-4 rounded-xl font-semibold shadow-lg transition-all duration-300 transform hover:-translate-y-0.5 ${
              isProcessing
                ? 'bg-gray-600 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 hover:shadow-xl'
            }`}
          >
            {isProcessing ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </div>
            ) : 'Generate Cinematic Teaser'}
          </button>
        </form>
      </div>

      {/* About Section */}
      <div className="w-full max-w-3xl bg-gradient-to-r from-purple-800/70 to-pink-800/70 backdrop-blur-md rounded-2xl shadow-lg p-8 text-center border border-purple-500/30">
        <h3 className="text-2xl font-bold mb-4 text-white">
          About Cinematic Teasers
        </h3>
        <p className="text-purple-200 leading-relaxed">
          Cinematic teasers capture the most visually compelling moments, creating
          dramatic previews that bring your story to life using advanced AI analysis
          of visual content and scene composition.
        </p>
      </div>
    </div>
  )
}

export default Cinematic