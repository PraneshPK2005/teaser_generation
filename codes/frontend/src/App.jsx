// App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Home from './pages/Home'
import Learning from './pages/Learning'
import Cinematic from './pages/Cinematic'
import Result from './pages/Result'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/learning" element={<Learning />} />
          <Route path="/cinematic" element={<Cinematic />} />
          <Route path="/result" element={<Result />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App