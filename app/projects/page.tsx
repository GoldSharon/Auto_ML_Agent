'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Link from 'next/link'
import { ArrowLeft, Trash2, RotateCcw, Eye } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Project {
  project_name: string
  created_at: string
  status: string
  best_model?: string
  evaluation_scores?: Record<string, any>
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const res = await fetch(`${API_URL}/api/projects`)
        if (res.ok) {
          const data = await res.json()
          setProjects(data.projects)
        }
      } catch (error) {
        console.error('Failed to fetch projects:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchProjects()
  }, [])

  const formatDate = (timestamp: string) => {
    try {
      return new Date(parseFloat(timestamp) * 1000).toLocaleDateString()
    } catch {
      return 'Unknown'
    }
  }

  const getStatusBadge = (status: string) => {
    const statusStyles = {
      completed: 'bg-green-900/30 text-green-300 border-green-600',
      training: 'bg-blue-900/30 text-blue-300 border-blue-600',
      failed: 'bg-red-900/30 text-red-300 border-red-600',
      queued: 'bg-yellow-900/30 text-yellow-300 border-yellow-600'
    }

    const style = statusStyles[status as keyof typeof statusStyles] || 'bg-slate-700 text-slate-300'
    return `inline-block px-3 py-1 rounded text-xs font-medium border ${style}`
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <nav className="border-b border-slate-700 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/" className="inline-flex items-center gap-2 text-slate-300 hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
          <Link href="/train">
            <Button className="bg-blue-600 hover:bg-blue-700">New Project</Button>
          </Link>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-16">
        <h1 className="text-4xl font-bold text-white mb-2">Projects</h1>
        <p className="text-slate-400 mb-8">View your trained models and results</p>

        {loading ? (
          <Card className="border-slate-700 bg-slate-800/50">
            <CardContent className="p-8 text-center">
              <p className="text-slate-300">Loading projects...</p>
            </CardContent>
          </Card>
        ) : projects.length === 0 ? (
          <Card className="border-slate-700 bg-slate-800/50">
            <CardContent className="p-8 text-center">
              <p className="text-slate-400 mb-4">No projects yet</p>
              <Link href="/train">
                <Button className="bg-blue-600 hover:bg-blue-700">Create First Project</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {projects.map((project) => (
              <Card key={project.project_name} className="border-slate-700 bg-slate-800/50 hover:bg-slate-800/70 transition-colors">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-white mb-2">{project.project_name}</h3>
                      <div className="flex flex-wrap items-center gap-4 text-sm">
                        <p className="text-slate-400">
                          Created: <span className="text-slate-300">{formatDate(project.created_at)}</span>
                        </p>
                        <span className={getStatusBadge(project.status)}>{project.status}</span>
                        {project.best_model && (
                          <p className="text-slate-400">
                            Best Model: <span className="text-blue-400">{project.best_model}</span>
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Evaluation Scores Preview */}
                  {project.evaluation_scores && Object.keys(project.evaluation_scores).length > 0 && (
                    <div className="mb-4 bg-slate-700/30 rounded p-3">
                      <p className="text-xs text-slate-400 font-semibold mb-2">Latest Scores (Top Model)</p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                        {Object.entries(project.evaluation_scores)
                          .slice(0, 1)
                          .map(([model, scores]: [string, any]) =>
                            Object.entries(scores)
                              .slice(0, 4)
                              .map(([metric, value]: [string, any]) => (
                                <div key={`${model}-${metric}`}>
                                  <p className="text-slate-500">{metric}</p>
                                  <p className="text-blue-400 font-semibold">
                                    {typeof value === 'number' ? value.toFixed(3) : value}
                                  </p>
                                </div>
                              ))
                          )}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Link href={`/project-details/${project.project_name}`} className="flex-1">
                      <Button variant="outline" className="w-full border-slate-600 text-slate-300 hover:bg-slate-700 bg-transparent">
                        <Eye className="w-4 h-4 mr-2" />
                        View Details
                      </Button>
                    </Link>

                    <Link href={`/predict/${project.project_name}`} className="flex-1">
                      <Button variant="outline" className="w-full border-slate-600 text-slate-300 hover:bg-slate-700 bg-transparent">
                        <RotateCcw className="w-4 h-4 mr-2" />
                        Re-predict
                      </Button>
                    </Link>

                    <Button variant="ghost" size="sm" className="text-red-400 hover:text-red-300 hover:bg-red-900/20">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
