'use client'

import React from "react"

import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import Link from 'next/link'
import { ArrowLeft, Upload } from 'lucide-react'
import { useRouter } from 'next/navigation'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface DataAnalysis {
  shape: [number, number]
  columns: string[]
  dtypes: Record<string, string>
  missing_values: Record<string, number>
  head: Record<string, any>[]
}

export default function TrainPage() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [step, setStep] = useState<'upload' | 'configure' | 'review'>('upload')
  const [file, setFile] = useState<File | null>(null)
  const [tempPath, setTempPath] = useState<string>('')
  const [analysis, setAnalysis] = useState<DataAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<string>('')

  // Form state
  const [projectName, setProjectName] = useState('')
  const [mlType, setMlType] = useState('SUPERVISED')
  const [learningType, setLearningType] = useState('REGRESSION')
  const [processingType, setProcessingType] = useState('TRAINING_ONLY')
  const [targetColumn, setTargetColumn] = useState('')
  const [testSize, setTestSize] = useState('0.2')
  const [hyperTuning, setHyperTuning] = useState(false)

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return

    setLoading(true)
    setMessage('')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const res = await fetch(`${API_URL}/api/upload`, {
        method: 'POST',
        body: formData
      })

      if (res.ok) {
        const data = await res.json()
        setFile(selectedFile)
        setTempPath(data.temp_path)

        // Analyze data
        const analyzeRes = await fetch(`${API_URL}/api/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ temp_path: data.temp_path })
        })

        if (analyzeRes.ok) {
          const analysisData = await analyzeRes.json()
          setAnalysis(analysisData)
          setStep('configure')
        }
      } else {
        setMessage('Failed to upload file')
      }
    } catch (error) {
      setMessage('Connection error. Make sure backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleStartTraining = async () => {
    if (!projectName || !targetColumn) {
      setMessage('Please fill in all required fields')
      return
    }

    setLoading(true)
    setMessage('')

    try {
      const res = await fetch(`${API_URL}/api/train`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: projectName,
          temp_path: tempPath,
          ml_type: mlType,
          learning_type: learningType,
          processing_type: processingType,
          target_column: targetColumn,
          test_size: parseFloat(testSize),
          hyper_parameter_tuning: hyperTuning
        })
      })

      if (res.ok) {
        const data = await res.json()
        router.push(`/training/${data.project_name}`)
      } else {
        setMessage('Failed to start training')
      }
    } catch (error) {
      setMessage('Connection error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <nav className="border-b border-slate-700 bg-slate-950/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <Link href="/" className="inline-flex items-center gap-2 text-slate-300 hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-6 py-16">
        {/* Step 1: Upload */}
        {step === 'upload' && (
          <Card className="border-slate-700 bg-slate-800/50">
            <CardHeader>
              <CardTitle className="text-white">Upload Dataset</CardTitle>
              <CardDescription className="text-slate-400">
                Select a CSV file to get started
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 transition-colors"
              >
                <Upload className="w-8 h-8 mx-auto mb-2 text-slate-400" />
                <p className="text-slate-300 mb-2">Click to upload or drag and drop</p>
                <p className="text-xs text-slate-500">CSV files only</p>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileSelect}
                className="hidden"
              />

              {file && <p className="text-sm text-green-400 mt-4">✓ {file.name} selected</p>}
              {message && <p className="text-sm text-red-400 mt-4">{message}</p>}

              <Button
                disabled={!file || loading}
                onClick={() => setStep('configure')}
                className="w-full mt-6 bg-blue-600 hover:bg-blue-700"
              >
                {loading ? 'Processing...' : 'Continue'}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Configure */}
        {step === 'configure' && analysis && (
          <Card className="border-slate-700 bg-slate-800/50">
            <CardHeader>
              <CardTitle className="text-white">Configure Training</CardTitle>
              <CardDescription className="text-slate-400">
                Dataset: {analysis.shape[0]} rows × {analysis.shape[1]} columns
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Project Name */}
                <div>
                  <Label className="text-slate-200">Project Name</Label>
                  <Input
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    placeholder="e.g., Housing Price Prediction"
                    className="bg-slate-700 border-slate-600 text-white mt-2"
                  />
                </div>

                {/* ML Type */}
                <div>
                  <Label className="text-slate-200">ML Type</Label>
                  <Select value={mlType} onValueChange={setMlType}>
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-700 border-slate-600">
                      <SelectItem value="SUPERVISED">Supervised</SelectItem>
                      <SelectItem value="UNSUPERVISED">Unsupervised</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Learning Type */}
                <div>
                  <Label className="text-slate-200">Learning Type</Label>
                  <Select value={learningType} onValueChange={setLearningType}>
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-700 border-slate-600">
                      <SelectItem value="REGRESSION">Regression</SelectItem>
                      <SelectItem value="CLASSIFICATION">Classification</SelectItem>
                      <SelectItem value="CLUSTERING">Clustering</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Target Column */}
                <div>
                  <Label className="text-slate-200">Target Column</Label>
                  <Select value={targetColumn} onValueChange={setTargetColumn}>
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white mt-2">
                      <SelectValue placeholder="Select target column" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-700 border-slate-600">
                      {analysis.columns.map((col) => (
                        <SelectItem key={col} value={col}>
                          {col}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Processing Type */}
                <div>
                  <Label className="text-slate-200">Processing Type</Label>
                  <Select value={processingType} onValueChange={setProcessingType}>
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-700 border-slate-600">
                      <SelectItem value="TRAINING_ONLY">Training Only</SelectItem>
                      <SelectItem value="PREPROCESS_TRAIN">Preprocessing + Training</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Test Size */}
                <div>
                  <Label className="text-slate-200">Test Size</Label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0.1"
                    max="0.5"
                    value={testSize}
                    onChange={(e) => setTestSize(e.target.value)}
                    className="bg-slate-700 border-slate-600 text-white mt-2"
                  />
                </div>

                {/* Hyper Tuning */}
                <div className="flex items-center gap-2">
                  <Checkbox
                    id="hyper-tuning"
                    checked={hyperTuning}
                    onCheckedChange={(checked) => setHyperTuning(checked as boolean)}
                    className="border-slate-600"
                  />
                  <Label htmlFor="hyper-tuning" className="text-slate-200 cursor-pointer">
                    Enable Hyperparameter Tuning
                  </Label>
                </div>

                {message && <p className="text-sm text-red-400">{message}</p>}

                <div className="flex gap-4 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setStep('upload')}
                    className="flex-1 border-slate-600 text-slate-300 hover:bg-slate-700"
                  >
                    Back
                  </Button>
                  <Button
                    onClick={handleStartTraining}
                    disabled={loading}
                    className="flex-1 bg-blue-600 hover:bg-blue-700"
                  >
                    {loading ? 'Starting...' : 'Start Training'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  )
}
