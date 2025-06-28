'use client'

import MCPConfig from '@/components/MCPConfig'
import { useAuth } from '@/contexts/AuthContext'
import { useTokens } from '@/hooks/useTokens'
import { copyToClipboard, formatDate } from '@/lib/utils'
import {
  BookOpen,
  Container,
  Copy,
  ExternalLink,
  Eye,
  EyeOff,
  Key,
  LogOut,
  Plus,
  Server,
  Settings,
  Trash2,
  User
} from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { toast } from 'react-hot-toast'

type TabType = 'tokens' | 'configuration' | 'docker' | 'resources'

export default function Dashboard() {
  const { user, signOut, loading: authLoading } = useAuth()
  const { tokens, loading: tokensLoading, generateToken, revokeToken } = useTokens()
  const router = useRouter()
  
  const [showTokenModal, setShowTokenModal] = useState(false)
  const [tokenName, setTokenName] = useState('')
  const [generatedToken, setGeneratedToken] = useState<string | null>(null)
  const [visibleTokens, setVisibleTokens] = useState<Set<string>>(new Set())
  const [generatingToken, setGeneratingToken] = useState(false)
  const [activeTab, setActiveTab] = useState<TabType>('tokens')

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/auth')
    }
  }, [user, authLoading, router])

  // Set default tab based on user state
  useEffect(() => {
    if (tokens.length === 0 && activeTab !== 'tokens' && activeTab !== 'resources') {
      setActiveTab('tokens')
    }
  }, [tokens.length, activeTab])

  if (authLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const handleGenerateToken = async () => {
    if (!tokenName.trim()) {
      toast.error('Please enter a token name')
      return
    }

    setGeneratingToken(true)
    try {
      const result = await generateToken(tokenName.trim())
      if (result.error) {
        toast.error(result.error)
      } else if (result.token) {
        setGeneratedToken(result.token)
        setTokenName('')
        toast.success('Token generated successfully!')
      }
    } catch {
      toast.error('Failed to generate token')
    } finally {
      setGeneratingToken(false)
    }
  }

  const handleRevokeToken = async (tokenId: string, tokenName: string) => {
    if (!confirm(`Are you sure you want to revoke the token "${tokenName}"? This action cannot be undone.`)) {
      return
    }

    try {
      const result = await revokeToken(tokenId)
      if (result.error) {
        toast.error(result.error)
      } else {
        toast.success('Token revoked successfully')
      }
    } catch {
      toast.error('Failed to revoke token')
    }
  }

  const handleCopyToken = async (token: string) => {
    try {
      await copyToClipboard(token)
      toast.success('Token copied to clipboard!')
    } catch {
      toast.error('Failed to copy token')
    }
  }

  const toggleTokenVisibility = (tokenId: string) => {
    const newVisible = new Set(visibleTokens)
    if (newVisible.has(tokenId)) {
      newVisible.delete(tokenId)
    } else {
      newVisible.add(tokenId)
    }
    setVisibleTokens(newVisible)
  }

  const handleSignOut = async () => {
    await signOut()
    router.push('/')
  }

  const dockerCommand = (token: string) => `docker run -d \\
  --name dhafnck-mcp \\
  -p 8000:8000 \\
  -e DHAFNCK_TOKEN="${token}" \\
  -v dhafnck-data:/data \\
  dhafnck/mcp-server:latest`

  const dockerBuildCommand = `# Build the Docker image from source
docker build -t dhafnck/mcp-server:latest .`

  const dockerDebugCommand = (token: string) => `# Debug mode with development features
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build \\
  -e DHAFNCK_TOKEN="${token}" \\
  -e FASTMCP_LOG_LEVEL=DEBUG \\
  -e FASTMCP_ENABLE_RICH_TRACEBACKS=1`

  const dockerStopCommand = `# Stop and remove container
docker stop dhafnck-mcp && docker rm dhafnck-mcp`

  const dockerLogsCommand = `# View container logs
docker logs -f dhafnck-mcp`

  const tabs = [
    {
      id: 'tokens' as TabType,
      label: 'API Tokens',
      icon: Key,
      count: tokens.length
    },
    {
      id: 'configuration' as TabType,
      label: 'Configuration',
      icon: Settings,
      disabled: tokens.length === 0
    },
    {
      id: 'docker' as TabType,
      label: 'Docker Setup',
      icon: Container,
      disabled: tokens.length === 0
    },
    {
      id: 'resources' as TabType,
      label: 'Resources',
      icon: BookOpen
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">DhafnckMCP</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="hidden sm:flex items-center text-sm text-gray-600">
                <User className="h-4 w-4 mr-2" />
                <span className="truncate max-w-48">{user.email}</span>
              </div>
              <button
                onClick={handleSignOut}
                className="flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                <LogOut className="h-4 w-4 mr-1" />
                <span className="hidden sm:inline">Sign out</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-4 sm:py-8 px-4 sm:px-6 lg:px-8">
        {/* Welcome Message */}
        <div className="mb-6 sm:mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
            Welcome back!
          </h2>
          <p className="text-gray-600">
            Manage your MCP server configuration and API tokens
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm border">
          {/* Tab Navigation */}
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-4 sm:px-6 overflow-x-auto" aria-label="Tabs">
              {tabs.map((tab) => {
                const IconComponent = tab.icon
                const isActive = activeTab === tab.id
                const isDisabled = tab.disabled
                
                return (
                  <button
                    key={tab.id}
                    onClick={() => !isDisabled && setActiveTab(tab.id)}
                    disabled={isDisabled}
                    className={`
                      whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors
                      ${isActive
                        ? 'border-blue-500 text-blue-600'
                        : isDisabled
                        ? 'border-transparent text-gray-300 cursor-not-allowed'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }
                    `}
                  >
                    <IconComponent className="h-4 w-4" />
                    <span>{tab.label}</span>
                    {tab.count !== undefined && (
                      <span className={`
                        ml-2 py-0.5 px-2 rounded-full text-xs
                        ${isActive ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'}
                      `}>
                        {tab.count}
                      </span>
                    )}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-4 sm:p-6">
            {/* Tokens Tab */}
            {activeTab === 'tokens' && (
              <div>
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">API Tokens</h3>
                    <p className="mt-1 text-sm text-gray-600">
                      Create and manage API tokens for your MCP server
                    </p>
                  </div>
                  <button
                    onClick={() => setShowTokenModal(true)}
                    className="mt-4 sm:mt-0 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center justify-center transition-colors"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Generate Token
                  </button>
                </div>

                {tokensLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                ) : tokens.length === 0 ? (
                  <div className="text-center py-12">
                    <Key className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No API tokens</h3>
                    <p className="text-gray-600 mb-6">
                      Generate your first token to start using the MCP server
                    </p>
                    <button
                      onClick={() => setShowTokenModal(true)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium transition-colors"
                    >
                      Generate Your First Token
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {tokens.map((token) => (
                      <div key={token.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-3">
                          <h4 className="font-medium text-gray-900 mb-2 sm:mb-0">{token.name}</h4>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => toggleTokenVisibility(token.id)}
                              className="text-gray-400 hover:text-gray-600 transition-colors p-1"
                              title={visibleTokens.has(token.id) ? 'Hide token' : 'Show token'}
                            >
                              {visibleTokens.has(token.id) ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </button>
                            <button
                              onClick={() => handleCopyToken(token.token)}
                              className="text-gray-400 hover:text-gray-600 transition-colors p-1"
                              title="Copy token"
                            >
                              <Copy className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleRevokeToken(token.id, token.name)}
                              className="text-red-400 hover:text-red-600 transition-colors p-1"
                              title="Revoke token"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                        
                        <div className="bg-gray-100 rounded p-3 mb-3 overflow-hidden">
                          <code className="text-sm font-mono text-gray-800 break-all">
                            {visibleTokens.has(token.id) 
                              ? token.token 
                              : '•'.repeat(32)
                            }
                          </code>
                        </div>
                        
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between text-xs text-gray-500 space-y-1 sm:space-y-0">
                          <span>Created: {formatDate(token.created_at)}</span>
                          {token.last_used && (
                            <span>Last used: {formatDate(token.last_used)}</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Configuration Tab */}
            {activeTab === 'configuration' && tokens.length > 0 && (
              <div>
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900">MCP Configuration</h3>
                  <p className="mt-1 text-sm text-gray-600">
                    Choose your environment and configure Cursor to connect to your MCP server
                  </p>
                </div>
                <MCPConfig
                  token={tokens[0].token}
                  showInstructions={true}
                  className="border-0 shadow-none"
                />
              </div>
            )}

            {/* Docker Setup Tab */}
            {activeTab === 'docker' && tokens.length > 0 && (
              <div>
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900">Docker Setup</h3>
                  <p className="mt-1 text-sm text-gray-600">
                    Run your MCP server locally using Docker with various deployment options
                  </p>
                </div>
                
                <div className="space-y-6">
                  {/* Quick Start */}
                  <div className="bg-gray-50 rounded-lg p-4 sm:p-6">
                    <h4 className="font-medium text-gray-900 mb-3">🚀 Quick Start (Recommended)</h4>
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Run Pre-built Image:
                      </label>
                      <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-gray-400">Terminal</span>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => toggleTokenVisibility('docker-config')}
                              className="text-gray-400 hover:text-white transition-colors"
                              title={visibleTokens.has('docker-config') ? 'Hide token' : 'Show token'}
                            >
                              {visibleTokens.has('docker-config') ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </button>
                            <button
                              onClick={() => handleCopyToken(dockerCommand(tokens[0].token))}
                              className="text-gray-400 hover:text-white transition-colors"
                              title="Copy Docker command"
                            >
                              <Copy className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                        <pre className="whitespace-pre-wrap break-all text-xs sm:text-sm">
                          {dockerCommand(visibleTokens.has('docker-config') ? tokens[0].token : '•'.repeat(32))}
                        </pre>
                      </div>
                    </div>
                  </div>

                  {/* Build from Source */}
                  <div className="bg-blue-50 rounded-lg p-4 sm:p-6">
                    <h4 className="font-medium text-blue-900 mb-3">🔨 Build from Source</h4>
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Build Docker Image:
                      </label>
                      <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-gray-400">Terminal</span>
                          <button
                            onClick={() => handleCopyToken(dockerBuildCommand)}
                            className="text-gray-400 hover:text-white transition-colors"
                            title="Copy build command"
                          >
                            <Copy className="h-4 w-4" />
                          </button>
                        </div>
                        <pre className="whitespace-pre-wrap break-all text-xs sm:text-sm">
                          {dockerBuildCommand}
                        </pre>
                      </div>
                    </div>
                    <p className="text-sm text-blue-800">
                      Run this command in the project root directory to build the Docker image from source code.
                    </p>
                  </div>

                  {/* Debug Mode */}
                  <div className="bg-yellow-50 rounded-lg p-4 sm:p-6">
                    <h4 className="font-medium text-yellow-900 mb-3">🐛 Debug Mode</h4>
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Development with Live Reload:
                      </label>
                      <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-gray-400">Terminal</span>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => toggleTokenVisibility('docker-debug')}
                              className="text-gray-400 hover:text-white transition-colors"
                              title={visibleTokens.has('docker-debug') ? 'Hide token' : 'Show token'}
                            >
                              {visibleTokens.has('docker-debug') ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </button>
                            <button
                              onClick={() => handleCopyToken(dockerDebugCommand(tokens[0].token))}
                              className="text-gray-400 hover:text-white transition-colors"
                              title="Copy debug command"
                            >
                              <Copy className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                        <pre className="whitespace-pre-wrap break-all text-xs sm:text-sm">
                          {dockerDebugCommand(visibleTokens.has('docker-debug') ? tokens[0].token : '•'.repeat(32))}
                        </pre>
                      </div>
                    </div>
                    <p className="text-sm text-yellow-800">
                      Includes verbose logging, rich tracebacks, and live code reload for development.
                    </p>
                  </div>

                  {/* Management Commands */}
                  <div className="bg-red-50 rounded-lg p-4 sm:p-6">
                    <h4 className="font-medium text-red-900 mb-3">⚙️ Management Commands</h4>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Stop Container:
                        </label>
                        <div className="bg-gray-900 text-green-400 p-3 rounded-lg font-mono text-sm overflow-x-auto">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-gray-400 text-xs">Terminal</span>
                            <button
                              onClick={() => handleCopyToken(dockerStopCommand)}
                              className="text-gray-400 hover:text-white transition-colors"
                              title="Copy stop command"
                            >
                              <Copy className="h-3 w-3" />
                            </button>
                          </div>
                          <pre className="whitespace-pre-wrap break-all text-xs">
                            {dockerStopCommand}
                          </pre>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          View Logs:
                        </label>
                        <div className="bg-gray-900 text-green-400 p-3 rounded-lg font-mono text-sm overflow-x-auto">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-gray-400 text-xs">Terminal</span>
                            <button
                              onClick={() => handleCopyToken(dockerLogsCommand)}
                              className="text-gray-400 hover:text-white transition-colors"
                              title="Copy logs command"
                            >
                              <Copy className="h-3 w-3" />
                            </button>
                          </div>
                          <pre className="whitespace-pre-wrap break-all text-xs">
                            {dockerLogsCommand}
                          </pre>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Next Steps */}
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h4 className="font-medium text-green-900 mb-2">📋 Next Steps:</h4>
                    <ol className="list-decimal list-inside space-y-2 text-sm text-green-800">
                      <li>Choose your deployment method above (Quick Start recommended for first-time users)</li>
                      <li>Server will be available at <code className="bg-green-100 px-1 rounded">localhost:8000</code></li>
                      <li>Go to the Configuration tab to set up Cursor</li>
                      <li>Start using AI-powered task management!</li>
                    </ol>
                  </div>
                </div>
              </div>
            )}

            {/* Resources Tab */}
            {activeTab === 'resources' && (
              <div>
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900">Resources & Documentation</h3>
                  <p className="mt-1 text-sm text-gray-600">
                    Helpful links and documentation for using DhafnckMCP
                  </p>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <a
                    href="https://github.com/dhafnck/dhafnck_mcp/blob/main/CURSOR_MCP_SETUP.md"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors group"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="bg-blue-100 p-2 rounded-lg">
                        <BookOpen className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">Setup Guide</h4>
                        <p className="text-sm text-gray-600">Complete Cursor MCP setup</p>
                      </div>
                    </div>
                    <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-gray-600" />
                  </a>
                  
                  <a
                    href="https://github.com/dhafnck/dhafnck_mcp"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors group"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="bg-gray-100 p-2 rounded-lg">
                        <Server className="h-5 w-5 text-gray-600" />
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">GitHub Repository</h4>
                        <p className="text-sm text-gray-600">Source code & issues</p>
                      </div>
                    </div>
                    <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-gray-600" />
                  </a>
                  
                  <a
                    href="#"
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors group"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="bg-green-100 p-2 rounded-lg">
                        <User className="h-5 w-5 text-green-600" />
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">Support</h4>
                        <p className="text-sm text-gray-600">Get help & support</p>
                      </div>
                    </div>
                    <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-gray-600" />
                  </a>
                  
                  <a
                    href="#"
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors group"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="bg-purple-100 p-2 rounded-lg">
                        <Settings className="h-5 w-5 text-purple-600" />
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">API Reference</h4>
                        <p className="text-sm text-gray-600">MCP tools reference</p>
                      </div>
                    </div>
                    <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-gray-600" />
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Token Generation Modal */}
      {showTokenModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Generate New Token</h3>
              <p className="mt-1 text-sm text-gray-600">
                Create a new API token for your MCP server
              </p>
            </div>
            
            <div className="p-6">
              {generatedToken ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your new token (copy it now - you won&apos;t see it again)
                  </label>
                  <div className="bg-gray-50 border rounded-lg p-3 mb-4">
                    <div className="flex items-center justify-between">
                      <code className="text-sm font-mono text-gray-800 break-all pr-2">
                        {generatedToken}
                      </code>
                      <button
                        onClick={() => handleCopyToken(generatedToken)}
                        className="ml-2 text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0"
                      >
                        <Copy className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  
                  {/* MCP Configuration in Modal */}
                  <div className="mb-4">
                    <MCPConfig
                      token={generatedToken}
                      showInstructions={false}
                      title="MCP Configuration for Cursor"
                      className="border-0 shadow-none bg-transparent"
                    />
                  </div>
                  
                  <div className="flex justify-end space-x-3">
                    <button
                      onClick={() => {
                        setShowTokenModal(false)
                        setGeneratedToken(null)
                        setActiveTab('configuration')
                      }}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                    >
                      Done
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <label htmlFor="tokenName" className="block text-sm font-medium text-gray-700 mb-2">
                    Token name
                  </label>
                  <input
                    type="text"
                    id="tokenName"
                    value={tokenName}
                    onChange={(e) => setTokenName(e.target.value)}
                    placeholder="e.g., My Development Token"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    onKeyPress={(e) => e.key === 'Enter' && handleGenerateToken()}
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Choose a descriptive name to identify this token
                  </p>
                  
                  <div className="flex justify-end space-x-3 mt-6">
                    <button
                      onClick={() => {
                        setShowTokenModal(false)
                        setTokenName('')
                      }}
                      className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleGenerateToken}
                      disabled={generatingToken || !tokenName.trim()}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {generatingToken ? 'Generating...' : 'Generate Token'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 