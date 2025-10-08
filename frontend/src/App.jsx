import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Sidebar from './components/sidebar/sidebar'
import Home from './components/pages/Home'
import MesDocuments from './components/pages/MesDocuments'
import Corbeille from './components/pages/Corbeille'
import ChatPage from './components/pages/ChatPage'
import PdfViewer from './components/pages/PdfViewer'

const App = () => {
  return (
    <Router>
      <div className="flex h-screen overflow-hidden">
        <Sidebar />

        <div className="flex-1 overflow-y-auto bg-gray-50 ">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/Accueil" element={<Home />} />
            <Route path="/MesDocuments" element={<MesDocuments />} />
            <Route path="/Corbeille" element={<Corbeille />} />
            <Route path="/Chat" element={<ChatPage />} />
            <Route path="/PdfViewer" element={<PdfViewer />} />
          </Routes>
        </div>
      </div>
    </Router>
  )
}

export default App
