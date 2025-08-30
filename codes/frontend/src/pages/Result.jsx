// pages/Result.jsx
import { useState, useEffect } from 'react'
import { useLocation, Link } from 'react-router-dom'

const Result = () => {
  const location = useLocation()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (location.state?.result) {
      setResult(location.state.result)
      setLoading(false)
    } else {
      // If no result was passed, try to fetch from API or show error
      setLoading(false)
    }
  }, [location.state])

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading your results...</p>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">No Results Found</h2>
        <p className="text-gray-600 mb-6">It seems there was an issue generating your teaser.</p>
        <Link 
          to="/" 
          className="bg-blue-600 text-white py-2 px-6 rounded-md hover:bg-blue-700"
        >
          Go Back Home
        </Link>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center text-gray-800 mb-2">
        Your Teaser is Ready!
      </h1>
      <p className="text-center text-gray-600 mb-8">
        Duration: {result.duration || 'N/A'} seconds
      </p>
      
      <div className="max-w-3xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
        <video 
          controls 
          src={result.s3_url} 
          className="w-full"
          poster={result.thumbnail_url || ''}
        >
          Your browser does not support the video tag.
        </video>
        
        <div className="p-6">
          <div className="flex flex-wrap gap-4 mb-6">
            <a
              href={result.s3_url}
              download
              className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-md text-center hover:bg-blue-700"
            >
              Download Teaser
            </a>
            <Link
              to="/"
              className="flex-1 bg-gray-200 text-gray-800 py-3 px-4 rounded-md text-center hover:bg-gray-300"
            >
              Create Another
            </Link>
          </div>
          
          <div className="border-t pt-4">
            <h3 className="font-semibold text-gray-800 mb-2">Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Teaser URL: </span>
                <a 
                  href={result.s3_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline block truncate"
                  title={result.s3_url}
                >
                  {result.s3_url}
                </a>
              </div>
              <div>
                <span className="text-gray-600">Method: </span>
                <span className="block truncate">{result.method || 'N/A'}</span>
              </div>
              {result.video_s3_url && (
                <div>
                  <span className="text-gray-600">Original Video: </span>
                  <a 
                    href={result.video_s3_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline block truncate"
                    title={result.video_s3_url}
                  >
                    {result.video_s3_url}
                  </a>
                </div>
              )}
              {result.audio_s3_url && (
                <div>
                  <span className="text-gray-600">Audio Source: </span>
                  <a 
                    href={result.audio_s3_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline block truncate"
                    title={result.audio_s3_url}
                  >
                    {result.audio_s3_url}
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {result.timestamps && result.timestamps.length > 0 && (
        <div className="max-w-3xl mx-auto mt-8">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Timestamps Used</h3>
          <div className="bg-gray-100 rounded-lg p-4">
            <ul className="space-y-2">
              {result.timestamps.map((timestamp, index) => {
                // Handle both array format [start, end] and object format {start, end}
                const start = Array.isArray(timestamp) ? timestamp[0] : timestamp.start;
                const end = Array.isArray(timestamp) ? timestamp[1] : timestamp.end;
                const duration = end - start;
                
                return (
                  <li key={index} className="flex justify-between text-sm">
                    <span>{start}s - {end}s</span>
                    <span className="text-gray-600">Duration: {duration.toFixed(2)}s</span>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export default Result