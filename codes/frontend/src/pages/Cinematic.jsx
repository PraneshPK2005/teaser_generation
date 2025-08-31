import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import VideoInput from '../components/VideoInput'

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


      const response = await fetch('http://localhost:8000/generate-teaser', {
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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black py-10 px-6 flex flex-col items-center text-white">
      <h1 className="text-4xl font-bold mb-6">
        Cinematic Teaser Generator
      </h1>

      <div className="w-full max-w-3xl bg-gray-800 shadow-lg rounded-2xl p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Video Input */}
          <VideoInput formData={formData} handleInputChange={handleInputChange} />

          {/* Length Controls */}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold mb-2">
                Maximum Length (seconds)
              </label>
              <input
                type="number"
                name="maxLength"
                value={formData.maxLength}
                onChange={handleInputChange}
                className="w-full border border-gray-600 rounded-lg px-3 py-2 bg-gray-700 text-white focus:ring-2 focus:ring-purple-400"
                min="10"
                max="300"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">
                Minimum Length (seconds)
              </label>
              <input
                type="number"
                name="minLength"
                value={formData.minLength}
                onChange={handleInputChange}
                className="w-full border border-gray-600 rounded-lg px-3 py-2 bg-gray-700 text-white focus:ring-2 focus:ring-purple-400"
                min="5"
                max="120"
              />
            </div>
          </div>

          {/* Method Selection */}
          <div>
            <label className="block text-sm font-semibold mb-2">
              Processing Method
            </label>
            <select
              name="method"
              value={formData.method}
              onChange={handleInputChange}
              className="w-full border border-gray-600 rounded-lg px-3 py-2 bg-gray-700 text-white focus:ring-2 focus:ring-purple-400"
            >
              <option value="cinematic_a">Cinematic Method A (Visual Appeal)</option>
              <option value="gemini">Gemini Method (Balanced Approach)</option>
            </select>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isProcessing}
            className={`w-full py-3 rounded-lg font-semibold shadow-md transition duration-300 ${
              isProcessing
                ? 'bg-gray-500 cursor-not-allowed'
                : 'bg-purple-600 hover:bg-purple-700'
            }`}
          >
            {isProcessing ? 'Processing...' : 'Generate Cinematic Teaser'}
          </button>
        </form>
      </div>

      {/* About Section */}
      <div className="w-full max-w-3xl mt-8 bg-gray-800 border border-gray-700 rounded-2xl shadow-md p-6 text-center">
        <h3 className="text-lg font-semibold mb-2 text-purple-300">
          About Cinematic Teasers
        </h3>
        <p className="text-gray-300">
          Cinematic teasers capture the most visually compelling moments, creating
          dramatic previews that bring your story to life.
        </p>
      </div>
    </div>
  )
}

export default Cinematic
