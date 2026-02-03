import { useState, useRef } from 'react'

function FileUpload({ onUpload, loading }) {
  const [dragActive, setDragActive] = useState(false)
  const [fileName, setFileName] = useState(null)
  const inputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file) => {
    const validTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    const validExtensions = ['.pdf', '.docx']
    const fileExt = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))
    
    if (!validTypes.includes(file.type) && !validExtensions.includes(fileExt)) {
      alert('Please upload a PDF or DOCX file')
      return
    }
    setFileName(file.name)
    onUpload(file)
  }

  const handleClick = () => {
    inputRef.current?.click()
  }

  return (
    <div
      className={`
        relative p-10 border-2 border-dashed rounded-2xl transition-all duration-200 cursor-pointer
        ${dragActive
          ? 'border-blue-500 bg-blue-500/10'
          : 'border-slate-600 hover:border-slate-500 bg-slate-800/30 hover:bg-slate-800/50'
        }
        ${loading ? 'pointer-events-none opacity-60' : ''}
      `}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx"
        onChange={handleChange}
        className="hidden"
      />

      <div className="flex flex-col items-center gap-4">
        {loading ? (
          <>
            <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
            <div className="text-center">
              <p className="text-white font-medium">Analyzing resume...</p>
              <p className="text-slate-400 text-sm mt-1">{fileName}</p>
            </div>
          </>
        ) : (
          <>
            <div className="w-16 h-16 bg-slate-700/50 rounded-2xl flex items-center justify-center">
              <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <div className="text-center">
              <p className="text-white font-medium">
                Drop your resume here or <span className="text-blue-400">browse</span>
              </p>
              <p className="text-slate-400 text-sm mt-1">PDF or DOCX files, up to 10MB</p>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default FileUpload
