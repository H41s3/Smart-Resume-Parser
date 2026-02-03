import { useState } from 'react'
import FileUpload from './components/FileUpload'
import ResumeDisplay from './components/ResumeDisplay'

function App() {
  const [resumeData, setResumeData] = useState(null)
  const [scoreData, setScoreData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleFileUpload = async (file) => {
    setLoading(true)
    setError(null)
    setResumeData(null)
    setScoreData(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/v1/parse?include_score=true', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (data.success) {
        setResumeData(data.data)
        setScoreData(data.score)
      } else {
        setError(data.error || 'Failed to parse resume')
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure the API is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setResumeData(null)
    setScoreData(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Smart Resume Parser</h1>
              <p className="text-sm text-slate-400">NLP-powered resume analysis</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-12">
        {!resumeData ? (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-10">
              <h2 className="text-3xl font-bold text-white mb-3">
                Extract insights from any resume
              </h2>
              <p className="text-slate-400 text-lg">
                Upload a PDF or DOCX resume and get structured data instantly
              </p>
            </div>

            <FileUpload onUpload={handleFileUpload} loading={loading} />

            {error && (
              <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
                <div className="flex items-center gap-3">
                  <svg className="w-5 h-5 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-red-400">{error}</p>
                </div>
              </div>
            )}

            {/* Features */}
            <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { icon: '👤', title: 'Contact Info', desc: 'Name, email, phone, LinkedIn' },
                { icon: '💼', title: 'Experience', desc: 'Jobs, titles, dates, highlights' },
                { icon: '🎓', title: 'Education', desc: 'Degrees, institutions, fields' },
              ].map((feature) => (
                <div key={feature.title} className="p-5 bg-slate-800/50 rounded-xl border border-slate-700/50">
                  <div className="text-2xl mb-3">{feature.icon}</div>
                  <h3 className="font-semibold text-white mb-1">{feature.title}</h3>
                  <p className="text-sm text-slate-400">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div>
            <button
              onClick={handleReset}
              className="mb-8 flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Upload another resume
            </button>
            <ResumeDisplay data={resumeData} score={scoreData} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700/50 mt-auto">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <p className="text-center text-slate-500 text-sm">
            Powered by FastAPI + spaCy NLP
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
