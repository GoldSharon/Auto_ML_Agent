'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Link from 'next/link'
import { ArrowLeft, Download } from 'lucide-react'
import { useParams } from 'next/navigation'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ProjectData {
  project_name: string
  created_at: string
  status: string
  config: Record<string, any>
  best_model?: string
  evaluation_scores?: Record<string, Record<string, number>>
}

export default function ProjectDetailsPage() {
  const params = useParams()
  const projectName = params.project as string

  const [project, setProject] = useState<ProjectData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const res = await fetch(`${API_URL}/api/project/${projectName}`)
        if (res.ok) {
          const data = await res.json()
          setProject(data)
        }
      } catch (error) {
        console.error('Failed to fetch project:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchProject()
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

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="max-w-7xl mx-auto px-6 py-16 text-center">
          <p className="text-slate-300">Loading project details...</p>
        </div>
      </main>
    )
  }

  if (!project) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <Link href="/projects" className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Projects
          </Link>
          <Card className="border-slate-700 bg-slate-800/50">
            <CardContent className="p-8 text-center">
              <p className="text-slate-300">Project not found</p>
            </CardContent>
          </Card>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <nav className="border-b border-slate-700 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/projects" className="inline-flex items-center gap-2 text-slate-300 hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to Projects
          </Link>
          <Button onClick={handleDownload} className="bg-blue-600 hover:bg-blue-700">
            <Download className="w-4 h-4 mr-2" />
            Download Scores
          </Button>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-16">
        <h1 className="text-4xl font-bold text-white mb-2">{project.project_name}</h1>
        <p className="text-slate-400 mb-8">
          Status: <span className="text-green-400 font-semibold">{project.status}</span>
        </p>

        {/* Configuration */}
        <Card className="border-slate-700 bg-slate-800/50 mb-8">
          <CardHeader>
            <CardTitle className="text-white">Configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <p className="text-slate-400 text-sm">ML Type</p>
                <p className="text-white text-lg font-semibold">{project.config.ml_type}</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Learning Type</p>
                <p className="text-white text-lg font-semibold">{project.config.learning_type}</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Target Column</p>
                <p className="text-white text-lg font-semibold">{project.config.target_column}</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Test Size</p>
                <p className="text-white text-lg font-semibold">{(project.config.test_size * 100).toFixed(0)}%</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Hardware</p>
                <p className="text-white text-lg font-semibold">{project.config.acceleration_hardware}</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Hyperparameter Tuning</p>
                <p className="text-white text-lg font-semibold">{project.config.hyper_parameter_tuning ? 'Yes' : 'No'}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Best Model */}
        {project.best_model && (
          <Card className="border-slate-700 bg-slate-800/50 mb-8">
            <CardHeader>
              <CardTitle className="text-white">Best Model</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-white text-2xl font-bold text-center py-8">{project.best_model}</p>
            </CardContent>
          </Card>
        )}

        {/* Evaluation Scores */}
        {project.evaluation_scores && Object.keys(project.evaluation_scores).length > 0 && (
          <Card className="border-slate-700 bg-slate-800/50">
            <CardHeader>
              <CardTitle className="text-white">Evaluation Scores</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {Object.entries(project.evaluation_scores).map(([model, scores]) => (
                  <div key={model} className="bg-slate-700/30 rounded-lg p-6">
                    <h3 className="text-white font-bold text-lg mb-4">{model}</h3>
                    <div className="grid md:grid-cols-3 gap-4">
                      {Object.entries(scores).map(([metric, value]) => (
                        <div key={metric} className="bg-slate-800 rounded p-4 border border-slate-700">
                          <p className="text-slate-400 text-sm font-medium">{metric}</p>
                          <p className="text-white text-2xl font-bold mt-2">
                            {typeof value === 'number' ? value.toFixed(4) : value}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  )
}
