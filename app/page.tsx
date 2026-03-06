'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Link from 'next/link'
import { Zap, Database, TrendingUp, History } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Page() {
  const [gpuStatus, setGpuStatus] = useState<string>('Checking...')
  const [envStatus, setEnvStatus] = useState<boolean>(false)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_URL}/api/health`)
        const data = await res.json()
        setGpuStatus(data.gpu_available ? `✓ GPU: ${data.gpu_name}` : '✗ CPU Mode')
      } catch (error) {
        setGpuStatus('✗ Backend unavailable')
      }
    }

    const checkEnv = async () => {
      try {
        const res = await fetch(`${API_URL}/api/env-status`)
        const data = await res.json()
        setEnvStatus(!data.needs_setup)
      } catch (error) {
        setEnvStatus(false)
      }
    }

    checkHealth()
    checkEnv()
  }, [])

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-slate-700 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Zap className="w-6 h-6 text-blue-400" />
            AutoML
          </h1>
          <Link href="/projects">
            <Button variant="outline" size="sm">
              <History className="w-4 h-4 mr-2" />
              Projects
            </Button>
          </Link>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-white mb-4">
            Intelligent Machine Learning
          </h2>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            Upload your CSV, configure your model, and let our AI handle the rest.
            Automatic preprocessing, training, and evaluation.
          </p>
        </div>

        {/* Status Cards */}
        <div className="grid md:grid-cols-2 gap-4 mb-12">
          <Card className="border-slate-700 bg-slate-800/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-white">System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-slate-300">
                  <span className="text-blue-400 font-semibold">{gpuStatus}</span>
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-700 bg-slate-800/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-white">LLM Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-300 mb-3">
                {envStatus ? '✓ Configured' : '✗ Setup Required'}
              </p>
              {!envStatus && (
                <Link href="/setup">
                  <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                    Configure LLM
                  </Button>
                </Link>
              )}
            </CardContent>
          </Card>
        </div>

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-lg p-8 text-center mb-12">
          <h3 className="text-2xl font-bold text-white mb-4">Ready to train?</h3>
          <p className="text-slate-300 mb-6 max-w-lg mx-auto">
            Start by uploading your dataset and selecting your machine learning task
          </p>
          <Link href="/train">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-lg">
              <Database className="w-5 h-5 mr-2" />
              Create New Project
            </Button>
          </Link>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          <Card className="border-slate-700 bg-slate-800/50 hover:bg-slate-800 transition-colors">
            <CardHeader>
              <Zap className="w-8 h-8 text-blue-400 mb-2" />
              <CardTitle className="text-white">Fast Training</CardTitle>
              <CardDescription className="text-slate-400">
                GPU-accelerated training with automatic fallback to CPU
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="border-slate-700 bg-slate-800/50 hover:bg-slate-800 transition-colors">
            <CardHeader>
              <Database className="w-8 h-8 text-blue-400 mb-2" />
              <CardTitle className="text-white">Smart Preprocessing</CardTitle>
              <CardDescription className="text-slate-400">
                LLM-powered data analysis and feature engineering
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="border-slate-700 bg-slate-800/50 hover:bg-slate-800 transition-colors">
            <CardHeader>
              <TrendingUp className="w-8 h-8 text-blue-400 mb-2" />
              <CardTitle className="text-white">Real-time Tracking</CardTitle>
              <CardDescription className="text-slate-400">
                Live progress updates via WebSocket connection
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </div>
    </main>
  )
}
