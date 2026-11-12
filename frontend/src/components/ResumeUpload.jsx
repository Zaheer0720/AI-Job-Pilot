import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, CheckCircle, Loader2 } from 'lucide-react'
import clsx from 'clsx'

export default function ResumeUpload({ onUpload, isLoading, isComplete }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0])
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: isLoading || isComplete,
  })

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <FileText className="text-blue-400" size={22} />
        Step 1: Upload Your Resume
      </h2>

      <div
        {...getRootProps()}
        className={clsx(
          'border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200',
          isDragActive && 'border-blue-500 bg-blue-950/30',
          !isDragActive && !isComplete && 'border-slate-700 hover:border-blue-600 hover:bg-slate-800/50',
          isComplete && 'border-green-600/50 bg-green-950/20',
          (isLoading || isComplete) && 'cursor-default',
        )}
      >
        <input {...getInputProps()} />

        {isLoading ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="animate-spin text-blue-400" size={40} />
            <p className="text-slate-300 font-medium">Uploading & analyzing with Gemini AI...</p>
            <p className="text-slate-500 text-sm">Extracting skills, experience, education...</p>
          </div>
        ) : isComplete ? (
          <div className="flex flex-col items-center gap-3">
            <CheckCircle className="text-green-400" size={40} />
            <p className="text-green-300 font-semibold">Resume analyzed successfully!</p>
            <p className="text-slate-400 text-sm">Scroll down to review your profile and configure job search</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <Upload className={clsx('size-10', isDragActive ? 'text-blue-400' : 'text-slate-500')} />
            <div>
              <p className="text-slate-200 font-semibold text-lg">
                {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
              </p>
              <p className="text-slate-500 mt-1">or click to browse files</p>
            </div>
            <p className="text-slate-600 text-sm">Supports PDF, DOCX, DOC, TXT</p>
          </div>
        )}
      </div>
    </div>
  )
}
