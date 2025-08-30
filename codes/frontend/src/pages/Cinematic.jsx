// pages/Cinematic.jsx
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
        Cinematic Teaser Generator
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
              <option value="cinematic_a">Cinematic Method A (Visual Appeal)</option>
              <option value="gemini">Gemini (Balanced Approach)</option>
            </select>
          </div>
          
          <button
            type="submit"
            disabled={isProcessing}
            className={`w-full py-3 px-4 rounded-md text-white font-medium ${
              isProcessing ? 'bg-purple-400' : 'bg-purple-600 hover:bg-purple-700'
            }`}
          >
            {isProcessing ? 'Processing...' : 'Generate Cinematic Teaser'}
          </button>
        </form>
      </div>
      
      <div className="max-w-2xl mx-auto mt-8 bg-purple-50 p-4 rounded-lg">
        <h3 className="font-semibold text-purple-800 mb-2">About Cinematic Teasers</h3>
        <p className="text-purple-700">
          Cinematic teasers focus on visual storytelling. They extract the most visually 
          compelling moments from your video to create dramatic, engaging previews that 
          capture the essence of your visual narrative.
        </p>
      </div>
    </div>
  )
}

export default Cinematic