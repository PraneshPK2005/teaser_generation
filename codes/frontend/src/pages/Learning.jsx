import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import VideoInput from '../components/VideoInput'

const Learning = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    source: 'youtube',
    youtubeUrl: '',
    videoFile: null,
    maxLength: 70,
    minLength: 60,
    method: 'learning_b'
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


    // Debug: Log data to verify before sending
    for (let [key, value] of submitData.entries()) {
      console.log(`${key}: ${value}`)
    }

    const response = await fetch('http://localhost:8000/generate-teaser', {
      method: 'POST',
      body: submitData,
      credentials: 'include',
    })

    if (!response.ok) {
      const errorData = await response.json()
      console.error('Backend error:', errorData)
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
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-blue-200 to-blue-300 py-10 px-6 flex flex-col items-center">
      <h1 className="text-4xl font-bold text-blue-800 mb-6">
        Learning Teaser Generator
      </h1>

      <div className="w-full max-w-3xl bg-white shadow-lg rounded-2xl p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Video Input */}
          <VideoInput formData={formData} handleInputChange={handleInputChange} />

          {/* Length Controls */}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Maximum Length (seconds)
              </label>
              <input
                type="number"
                name="maxLength"
                value={formData.maxLength}
                onChange={handleInputChange}
                className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-400"
                min="10"
                max="300"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Minimum Length (seconds)
              </label>
              <input
                type="number"
                name="minLength"
                value={formData.minLength}
                onChange={handleInputChange}
                className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-400"
                min="5"
                max="120"
              />
            </div>
          </div>

          {/* Method Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Processing Method
            </label>
            <select
              name="method"
              value={formData.method}
              onChange={handleInputChange}
              className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-400"
            >
              <option value="learning_a">Learning Method A (Engaging Dialogue)</option>
              <option value="learning_b">Learning Method B (Key Points & Summary)</option>
            </select>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isProcessing}
            className={`w-full py-3 rounded-lg font-semibold text-white shadow-md transition duration-300 ${
              isProcessing
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isProcessing ? 'Processing...' : 'Generate Learning Teaser'}
          </button>
        </form>
      </div>

      {/* About Section */}
      <div className="w-full max-w-3xl mt-8 bg-blue-50 border border-blue-200 rounded-2xl shadow-md p-6 text-center">
        <h3 className="text-lg font-semibold text-blue-700 mb-2">
          About Learning Teasers
        </h3>
        <p className="text-gray-700">
          Learning teasers are perfect for educational content. They highlight key concepts
          and summaries to create engaging and informative previews for your audience.
        </p>
      </div>
    </div>
  )
}

export default Learning
