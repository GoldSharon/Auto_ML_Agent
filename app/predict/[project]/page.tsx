'use client'

import React from "react"

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import Link from 'next/link'
import { ArrowLeft, Upload } from 'lucide-react'
import { useParams } from 'next/navigation'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ProjectConfig {
  feature_columns: string[]
  input_format: string
}

export default function PredictPage() {
  const params = useParams()
  const projectName = params.project as string

  const [config, setConfig] = useState<ProjectConfig | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [predictions, setPredictions] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  const [predicting, setPredicting] = useState(false)
  const [message, setMessage] = useState<string>('')

  useEffect(() => {
    const fetchProjectConfig = async () => {
      try {
        const res = await fetch(`${API_URL}/api/project/${projectName}`)
        if (res.ok) {
          const data = await res.json()
          setConfig({
            feature_columns: Object.keys(data.config || {}),
            input_format: 'csv'
          })
        }
      } catch (error) {
        console.error('Failed to fetch project:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchProjectConfig()
  }, [projectName])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  const handlePredict = async () => {
    if (!file) {
      setMessage('Please select a file')
      return
    }

    setPredicting(true)
    setMessage('')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('project_name', projectName)

      const res = await fetch(`${API_URL}/api/predict`, {
        method: 'POST',
        body: formData
      })

      if (res.ok) {
        const data = await res.json()
        setPredictions(data)
        setMessage('Predictions completed successfully!')
      } else {
        setMessage('Prediction failed')
      }
    } catch (error) {
      setMessage('Connection error')
    } finally {
      setPredicting(false)
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="max-w-7xl mx-auto px-6 py-16 text-center">
          <p className="text-slate-300">Loading project...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <nav className="border-b border-slate-700 bg-slate-950/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <Link href="/projects" className="inline-flex items-center gap-2 text-slate-300 hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to Projects
          </Link>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-16">
        <h1 className="text-4xl font-bold text-white mb-8">Make Predictions</h1>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Upload Section */}
          <Card className="border-slate-700 bg-slate-800/50">
            <CardHeader>
              <CardTitle className="text-white">Upload Data</CardTitle>
              <CardDescription className="text-slate-400">
                Upload a CSV file with the same format as your training data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div
                  onClick={() => document.getElementById('file-input')?.click()}
                  className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 transition-colors"
                >
                  <Upload className="w-8 h-8 mx-auto mb-2 text-slate-400" />
                  <p className="text-slate-300 mb-2">Click to upload or drag and drop</p>
                  <p className="text-xs text-slate-500">CSV files only</p>
                </div>

                <input
                  id="file-input"
                  type="file"
                  accept=".csv"
                  onChange={handleFileSelect}
                  className="hidden"
                />

                {file && (
                  <div className="bg-green-900/20 border border-green-600 rounded p-3">
                    <p className="text-green-300 text-sm">✓ {file.name}</p>
                  </div>
                )}

                {message && (
                  <div className={`rounded p-3 text-sm ${message.includes('successfully') ? 'bg-green-900/20 text-green-300 border border-green-600' : 'bg-red-900/20 text-red-300 border border-red-600'}`}>
                    {message}
                  </div>
                )}

                <Button
                  onClick={handlePredict}
                  disabled={!file || predicting}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  {predicting ? 'Predicting...' : 'Make Predictions'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Results Section */}
          {predictions && (
            <Card className="border-slate-700 bg-slate-800/50">
              <CardHeader>
                <CardTitle className="text-white">Predictions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {Array.isArray(predictions) ? (
                    predictions.slice(0, 10).map((pred, idx) => (
                      <div key={idx} className="bg-slate-700/30 rounded p-3">
                        <p className="text-slate-400 text-xs">Sample {idx + 1}</p>
                        <p className="text-white font-semibold mt-1">
                          {typeof pred === 'number' ? pred.toFixed(4) : pred}
                        </p>
                      </div>
                    ))
                  ) : (
                    <div className="bg-slate-700/30 rounded p-3">
                      <pre className="text-slate-300 text-xs overflow-x-auto">
                        {JSON.stringify(predictions, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
                {Array.isArray(predictions) && predictions.length > 10 && (
                  <p className="text-slate-400 text-sm mt-4">
                    +{predictions.length - 10} more predictions...
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </main>
  )
}
