// components/VideoInput.jsx
const VideoInput = ({ formData, handleInputChange }) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Video Source
        </label>
        <div className="flex space-x-4">
          <label className="inline-flex items-center">
            <input
              type="radio"
              name="source"
              value="youtube"
              checked={formData.source === 'youtube'}
              onChange={handleInputChange}
              className="text-blue-600"
            />
            <span className="ml-2">YouTube URL</span>
          </label>
          <label className="inline-flex items-center">
            <input
              type="radio"
              name="source"
              value="upload"
              checked={formData.source === 'upload'}
              onChange={handleInputChange}
              className="text-blue-600"
            />
            <span className="ml-2">Upload Video</span>
          </label>
        </div>
      </div>

      {formData.source === 'youtube' ? (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            YouTube URL
          </label>
          <input
            type="url"
            name="youtubeUrl"
            value={formData.youtubeUrl}
            onChange={handleInputChange}
            placeholder="https://www.youtube.com/watch?v=..."
            className="w-full p-2 border border-gray-300 rounded-md"
            required
          />
        </div>
      ) : (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Video File
          </label>
          <div className="flex items-center justify-center w-full">
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <svg className="w-8 h-8 mb-4 text-gray-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                  <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                </svg>
                <p className="mb-2 text-sm text-gray-500">
                  <span className="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-gray-500">MP4, AVI, MOV (MAX. 500MB)</p>
              </div>
              <input 
                type="file" 
                name="videoFile" 
                onChange={handleInputChange} 
                className="hidden" 
                accept="video/mp4,video/avi,video/quicktime"
                required={formData.source === 'upload'}
              />
            </label>
          </div>
          {formData.videoFile && (
            <p className="mt-2 text-sm text-gray-600">
              Selected: {formData.videoFile.name}
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default VideoInput