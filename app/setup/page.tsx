'use client'

import React from "react"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import { useRouter } from 'next/navigation'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function SetupPage() {
  const router = useRouter()
  const [llmModel, setLlmModel] = useState('')
  const [llmApiKey, setLlmApiKey] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)

    try {
      const res = await fetch(`${API_URL}/api/setup-llm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ llm_model: llmModel, llm_api_key: llmApiKey })
      })

      if (res.ok) {
        setMessage({ type: 'success', text: 'LLM configured successfully!' })
        setTimeout(() => router.push('/'), 2000)
      } else {
        setMessage({ type: 'error', text: 'Failed to configure LLM' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Connection error. Make sure backend is running.' })
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

      <div className="max-w-md mx-auto px-6 py-16">
        <Card className="border-slate-700 bg-slate-800/50">
          <CardHeader>
            <CardTitle className="text-white">Setup LLM Configuration</CardTitle>
            <CardDescription className="text-slate-400">
              Configure your LLM model and API key for data preprocessing
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="llm-model" className="text-slate-200">
                  LLM Model Name
                </Label>
                <Input
                  id="llm-model"
                  placeholder="e.g., gpt-4, claude-3-opus, etc."
                  value={llmModel}
                  onChange={(e) => setLlmModel(e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white mt-2"
                  required
                />
              </div>

              <div>
                <Label htmlFor="llm-api" className="text-slate-200">
                  LLM API Key
                </Label>
                <Input
                  id="llm-api"
                  type="password"
                  placeholder="Your API key"
                  value={llmApiKey}
                  onChange={(e) => setLlmApiKey(e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white mt-2"
                  required
                />
              </div>

              {message && (
                <div className={`p-3 rounded text-sm ${message.type === 'success' ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'}`}>
                  {message.text}
                </div>
              )}

              <Button
                type="submit"
                disabled={loading || !llmModel || !llmApiKey}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                {loading ? 'Saving...' : 'Save Configuration'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
