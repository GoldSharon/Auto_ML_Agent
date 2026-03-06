'use client'

import { useEffect, useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Link from 'next/link'
import { ArrowLeft, Download, Loader } from 'lucide-react'
import { useParams } from 'next/navigation'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface TrainingMessage {
  type: 'status' | 'error' | 'complete'
  message: string
  progress?: number
  result?: any
  error?: string
}

export default function TrainingPage() {
  const params = useParams()
  const projectName = params.project as string
  const wsRef = useRef<WebSocket | null>(null)

  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('Initializing...')
  const [completed, setCompleted] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<any>(null)
  const [logs, setLogs] = useState<string[]>([])

  useEffect(() => {
    // Connect to WebSocket - use backend URL from API_URL
    const wsProtocol = API_URL.startsWith('https') ? 'wss:' : 'ws:'
    const backendHost = API_URL.replace('http://', '').replace('https://', '')
    const wsUrl = `${wsProtocol}//${backendHost}/ws/${projectName}`

    wsRef.current = new WebSocket(wsUrl)

    wsRef.current.onopen = () => {
      console.log('WebSocket connected')
      wsRef.current?.send(JSON.stringify({ type: 'subscribe', project: projectName }))
    }

    wsRef.current.onmessage = (event) => {
      const message: TrainingMessage = JSON.parse(event.data)

      setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${message.message}`])

      if (message.type === 'status') {
        setStatus(message.message)
        if (message.progress) {
          setProgress(message.progress)
        }
      } else if (message.type === 'complete') {
        setProgress(100)
        setStatus('Training Complete!')
        setCompleted(true)
        setResult(message.result)
      } else if (message.type === 'error') {
        setError(message.message || message.error)
        setStatus('Training Failed')
      }
    }

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error)
      setError('WebSocket connection error')
    }

    wsRef.current.onclose = () => {
      console.log('WebSocket closed')
    }

    return () => {
      wsRef.current?.close()
    }
  }, [projectName])

  const handleDownload = async () => {
    try {
      const res = await fetch(`${API_URL}/api/project/${projectName}/download`)
      if (res.ok) {
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${projectName}_evaluation_scores.json`
        a.click()
      }
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-50">
      <nav className="border-b border-blue-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/" className="inline-flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors font-semibold">
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
          {completed && (
            <Button onClick={handleDownload} className="bg-green-600 hover:bg-green-700 text-white">
              <Download className="w-4 h-4 mr-2" />
              Download Results
            </Button>
          )}
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Main Status Card */}
        <Card className="border-blue-200 bg-white shadow-lg mb-8">
          <CardHeader className="border-b border-blue-100">
            <CardTitle className="text-gray-900 text-3xl">{projectName}</CardTitle>
            <CardDescription className="text-gray-600 text-base mt-2">Real-time Training Progress</CardDescription>
          </CardHeader>
          <CardContent className="pt-8">
            {/* Progress Bar */}
            <div className="mb-8">
              <div className="flex justify-between mb-3">
                <span className="text-gray-700 font-semibold">{status}</span>
                <span className="text-blue-600 font-bold text-lg">{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden shadow-sm">
                <div
                  className="bg-gradient-to-r from-blue-500 to-indigo-600 h-full transition-all duration-500 shadow-md"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Status Indicators */}
            {error && (
              <div className="bg-red-50 border-2 border-red-300 rounded-lg p-5 text-red-700 mb-6 flex items-start gap-4">
                <span className="text-2xl">⚠️</span>
                <div>
                  <p className="font-bold text-lg">Training Error</p>
                  <p className="text-sm mt-2 text-red-600">{error}</p>
                </div>
              </div>
            )}

            {completed && (
              <div className="bg-green-50 border-2 border-green-300 rounded-lg p-5 text-green-700 mb-6 flex items-start gap-4">
                <span className="text-2xl">✓</span>
                <div>
                  <p className="font-bold text-lg">Training Complete</p>
                  <p className="text-sm mt-2 text-green-600">All models trained and evaluated successfully</p>
                </div>
              </div>
            )}

            {!completed && !error && (
              <div className="flex items-center gap-3 text-blue-600 mb-6 bg-blue-50 p-4 rounded-lg">
                <Loader className="w-5 h-5 animate-spin" />
                <span className="font-medium">Training models in progress...</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results */}
        {result && completed && (
          <Card className="border-green-200 bg-white shadow-lg mb-8">
            <CardHeader className="border-b border-green-100">
              <CardTitle className="text-gray-900 text-2xl">Training Results</CardTitle>
            </CardHeader>
            <CardContent className="pt-8">
              <div className="space-y-6">
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
                  <p className="text-gray-600 text-sm font-semibold uppercase tracking-wide">Best Performing Model</p>
                  <p className="text-gray-900 text-2xl font-bold mt-2">{result.best_model?.toUpperCase()}</p>
                </div>

                {result.evaluation_scores && (
                  <div>
                    <p className="text-gray-900 text-lg font-bold mb-4">Performance Metrics</p>
                    <div className="grid gap-3">
                      {Object.entries(result.evaluation_scores).map(([model, scores]: [string, any]) => (
                        <div key={model} className="bg-white border-2 border-gray-200 rounded-lg p-5 hover:border-blue-300 transition-colors">
                          <p className="text-gray-900 font-bold text-lg capitalize">{model}</p>
                          <div className="text-sm text-gray-700 mt-3 space-y-2">
                            {Object.entries(scores).map(([metric, value]: [string, any]) => (
                              <p key={metric} className="flex justify-between">
                                <span className="text-gray-600">{metric}:</span>
                                <span className="font-semibold text-blue-600">{typeof value === 'number' ? value.toFixed(4) : value}</span>
                              </p>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Live Logs */}
        <Card className="border-gray-200 bg-white shadow-lg">
          <CardHeader className="border-b border-gray-200">
            <CardTitle className="text-gray-900 text-2xl">Live Training Logs</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="bg-gray-900 rounded-lg p-6 h-80 overflow-y-auto font-mono text-sm border-2 border-gray-300 shadow-inner">
              {logs.length === 0 ? (
                <p className="text-gray-500 italic">Waiting for training logs...</p>
              ) : (
                logs.map((log, idx) => (
                  <p key={idx} className="text-green-400 leading-relaxed">
                    {log}
                  </p>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
