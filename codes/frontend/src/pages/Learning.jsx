// pages/Learning.jsx
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

  // In both Learning.jsx and Cinematic.jsx, update the handleSubmit function
const handleSubmit = async (e) => {
  e.preventDefault()
  setIsProcessing(true)
  
  try {
    // Prepare form data for API call
    const submitData = new FormData()
    submitData.append('method', formData.method)
    submitData.append('max_length', formData.maxLength)
    submitData.append('min_length', formData.minLength)
    
    if (formData.source === 'youtube') {
      submitData.append('youtube_url', formData.youtubeUrl)
    } else {
      submitData.append('video_file', formData.videoFile)
    }

    // Call FastAPI endpoint
    const response = await fetch('http://127.0.0.1:8000/generate-teaser', {
      method: 'POST',
      body: submitData
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Failed to generate teaser')
    }
    
    const result = await response.json()
    
    // Navigate to result page with the response
    navigate('/result', { state: { result } })
  } catch (error) {
    console.error('Error generating teaser:', error)
    alert(`Failed to generate teaser: ${error.message}`)
  } finally {
    setIsProcessing(false)
  }
}

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center text-gray-800 mb-8">
        Learning Teaser Generator
      </h1>
      
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <VideoInput 
            formData={formData} 
            handleInputChange={handleInputChange} 
          />
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Maximum Length (seconds)
              </label>
              <input
                type="number"
                name="maxLength"
                value={formData.maxLength}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded-md"
                min="10"
                max="300"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Minimum Length (seconds)
              </label>
              <input
                type="number"
                name="minLength"
                value={formData.minLength}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded-md"
                min="5"
                max="120"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Processing Method
            </label>
            <select
              name="method"
              value={formData.method}
              onChange={handleInputChange}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="learning_a">Learning Method A (Engaging Dialogue)</option>
              <option value="learning_b">Learning Method B (Key Points & Summary)</option>
            </select>
          </div>
          
          <button
            type="submit"
            disabled={isProcessing}
            className={`w-full py-3 px-4 rounded-md text-white font-medium ${
              isProcessing ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isProcessing ? 'Processing...' : 'Generate Learning Teaser'}
          </button>
        </form>
      </div>
      
      <div className="max-w-2xl mx-auto mt-8 bg-blue-50 p-4 rounded-lg">
        <h3 className="font-semibold text-blue-800 mb-2">About Learning Teasers</h3>
        <p className="text-blue-700">
          Learning teasers are perfect for educational content. They focus on extracting 
          key concepts, summaries, and the most informative parts of your video to create 
          compelling previews that educate and engage viewers.
        </p>
      </div>
    </div>
  )
}

export default Learning