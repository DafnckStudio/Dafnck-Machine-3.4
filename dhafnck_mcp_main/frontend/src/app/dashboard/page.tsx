'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useTokens } from '@/hooks/useTokens'
import { copyToClipboard, formatDate } from '@/lib/utils'
import {
  Container,
  Copy,
  ExternalLink,
  Eye,
  EyeOff,
  Key,
  LogOut,
  Plus,
  Trash2,
  User
} from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { toast } from 'react-hot-toast'

export default function Dashboard() {
  const { user, signOut, loading: authLoading } = useAuth()
  const { tokens, loading: tokensLoading, generateToken, revokeToken } = useTokens()
  const router = useRouter()
  
  const [showTokenModal, setShowTokenModal] = useState(false)
  const [tokenName, setTokenName] = useState('')
  const [generatedToken, setGeneratedToken] = useState<string | null>(null)
  const [visibleTokens, setVisibleTokens] = useState<Set<string>>(new Set())
  const [generatingToken, setGeneratingToken] = useState(false)

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/auth')
    }
  }, [user, authLoading, router])

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
    } catch (error) {
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
    } catch (error) {
      toast.error('Failed to revoke token')
    }
  }

  const handleCopyToken = async (token: string) => {
    try {
      await copyToClipboard(token)
      toast.success('Token copied to clipboard!')
    } catch (error) {
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

  const mcpConfig = (token: string) => `{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "DHAFNCK_TOKEN=${token}",
        "-v", "dhafnck-data:/data",
        "dhafnck/mcp-server:latest"
      ],
      "env": {
        "DHAFNCK_TOKEN": "${token}"
      }
    }
  }
}`

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
              <div className="flex items-center text-sm text-gray-600">
                <User className="h-4 w-4 mr-2" />
                {user.email}
              </div>
              <button
                onClick={handleSignOut}
                className="flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                <LogOut className="h-4 w-4 mr-1" />
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Token Management */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-6 border-b">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Key className="h-5 w-5 text-gray-400 mr-2" />
                    <h2 className="text-lg font-semibold text-gray-900">API Tokens</h2>
                  </div>
                  <button
                    onClick={() => setShowTokenModal(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center transition-colors"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Generate Token
                  </button>
                </div>
                <p className="mt-1 text-sm text-gray-600">
                  Create and manage API tokens for your MCP server
                </p>
              </div>

              <div className="p-6">
                {tokensLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                ) : tokens.length === 0 ? (
                  <div className="text-center py-8">
                    <Key className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No API tokens</h3>
                    <p className="text-gray-600 mb-4">
                      Generate your first token to start using the MCP server
                    </p>
                    <button
                      onClick={() => setShowTokenModal(true)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                    >
                      Generate Token
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {tokens.map((token) => (
                      <div key={token.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-medium text-gray-900">{token.name}</h3>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => toggleTokenVisibility(token.id)}
                              className="text-gray-400 hover:text-gray-600 transition-colors"
                            >
                              {visibleTokens.has(token.id) ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </button>
                            <button
                              onClick={() => handleCopyToken(token.token)}
                              className="text-gray-400 hover:text-gray-600 transition-colors"
                            >
                              <Copy className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleRevokeToken(token.id, token.name)}
                              className="text-red-400 hover:text-red-600 transition-colors"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                        
                        <div className="bg-gray-50 rounded p-3 mb-2">
                          <code className="text-sm font-mono text-gray-800">
                            {visibleTokens.has(token.id) 
                              ? token.token 
                              : '•'.repeat(32)
                            }
                          </code>
                        </div>
                        
                        <div className="flex items-center justify-between text-xs text-gray-500">
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
            </div>
          </div>

          {/* Getting Started */}
          <div className="space-y-6">
            {/* Docker Instructions */}
            {tokens.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="p-6 border-b">
                  <div className="flex items-center">
                    <Container className="h-5 w-5 text-gray-400 mr-2" />
                    <h2 className="text-lg font-semibold text-gray-900">Docker Setup</h2>
                  </div>
                  <p className="mt-1 text-sm text-gray-600">
                    Run your MCP server locally
                  </p>
                </div>
                <div className="p-6">
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
                    <pre className="whitespace-pre-wrap break-all">
                      {dockerCommand(visibleTokens.has('docker-config') ? tokens[0].token : '•'.repeat(32))}
                    </pre>
                  </div>
                  <div className="mt-4 text-sm text-gray-600">
                    <p className="mb-2">After running the command:</p>
                    <ol className="list-decimal list-inside space-y-1">
                      <li>Server will be available at <code className="bg-gray-100 px-1 rounded">localhost:8000</code></li>
                      <li>Configure Cursor to connect to your MCP server</li>
                      <li>Start using AI-powered task management</li>
                    </ol>
                  </div>
                </div>
              </div>
            )}

            {/* MCP Configuration */}
            {tokens.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="p-6 border-b">
                  <div className="flex items-center">
                    <Key className="h-5 w-5 text-gray-400 mr-2" />
                    <h2 className="text-lg font-semibold text-gray-900">MCP Configuration</h2>
                  </div>
                  <p className="mt-1 text-sm text-gray-600">
                    Add this to your Cursor settings
                  </p>
                </div>
                <div className="p-6">
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Add to your <code className="bg-gray-100 px-1 rounded">mcp.json</code> file:
                    </label>
                    <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                                             <div className="flex items-center justify-between mb-2">
                         <span className="text-gray-400">mcp.json</span>
                         <div className="flex items-center space-x-2">
                           <button
                             onClick={() => toggleTokenVisibility('mcp-config')}
                             className="text-gray-400 hover:text-white transition-colors"
                             title={visibleTokens.has('mcp-config') ? 'Hide token' : 'Show token'}
                           >
                             {visibleTokens.has('mcp-config') ? (
                               <EyeOff className="h-4 w-4" />
                             ) : (
                               <Eye className="h-4 w-4" />
                             )}
                           </button>
                           <button
                             onClick={() => handleCopyToken(mcpConfig(tokens[0].token))}
                             className="text-gray-400 hover:text-white transition-colors"
                             title="Copy MCP configuration"
                           >
                             <Copy className="h-4 w-4" />
                           </button>
                         </div>
                       </div>
                       <pre className="whitespace-pre-wrap break-all text-xs">
                         {mcpConfig(visibleTokens.has('mcp-config') ? tokens[0].token : '•'.repeat(32))}
                       </pre>
                    </div>
                  </div>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="font-medium text-blue-900 mb-2">Setup Instructions:</h4>
                    <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800">
                      <li>Copy the configuration above</li>
                      <li>Open Cursor settings (Cmd/Ctrl + ,)</li>
                      <li>Search for "MCP" or navigate to Extensions → MCP</li>
                      <li>Add the configuration to your <code className="bg-blue-100 px-1 rounded">mcp.json</code> file</li>
                      <li>Restart Cursor to load the MCP server</li>
                      <li>Your DhafnckMCP tools will be available in the chat</li>
                    </ol>
                  </div>
                </div>
              </div>
            )}

            {/* Documentation */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-6 border-b">
                <h2 className="text-lg font-semibold text-gray-900">Resources</h2>
              </div>
              <div className="p-6 space-y-4">
                <a
                  href="#"
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div>
                    <h3 className="font-medium text-gray-900">Documentation</h3>
                    <p className="text-sm text-gray-600">Complete setup and usage guide</p>
                  </div>
                  <ExternalLink className="h-4 w-4 text-gray-400" />
                </a>
                
                <a
                  href="https://github.com/dhafnck/dhafnck_mcp"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div>
                    <h3 className="font-medium text-gray-900">GitHub Repository</h3>
                    <p className="text-sm text-gray-600">Source code and issues</p>
                  </div>
                  <ExternalLink className="h-4 w-4 text-gray-400" />
                </a>
                
                <a
                  href="#"
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div>
                    <h3 className="font-medium text-gray-900">Support</h3>
                    <p className="text-sm text-gray-600">Get help and support</p>
                  </div>
                  <ExternalLink className="h-4 w-4 text-gray-400" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Token Generation Modal */}
      {showTokenModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full">
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
                    Your new token (copy it now - you won't see it again)
                  </label>
                  <div className="bg-gray-50 border rounded-lg p-3 mb-4">
                    <div className="flex items-center justify-between">
                      <code className="text-sm font-mono text-gray-800 break-all">
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
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      MCP Configuration for Cursor:
                    </label>
                    <div className="bg-gray-900 text-green-400 p-3 rounded-lg font-mono text-xs overflow-x-auto max-h-40 overflow-y-auto">
                                             <div className="flex items-center justify-between mb-2">
                         <span className="text-gray-400">mcp.json</span>
                         <div className="flex items-center space-x-2">
                           <button
                             onClick={() => toggleTokenVisibility('modal-mcp-config')}
                             className="text-gray-400 hover:text-white transition-colors"
                             title={visibleTokens.has('modal-mcp-config') ? 'Hide token' : 'Show token'}
                           >
                             {visibleTokens.has('modal-mcp-config') ? (
                               <EyeOff className="h-4 w-4" />
                             ) : (
                               <Eye className="h-4 w-4" />
                             )}
                           </button>
                           <button
                             onClick={() => handleCopyToken(mcpConfig(generatedToken))}
                             className="text-gray-400 hover:text-white transition-colors"
                             title="Copy MCP configuration"
                           >
                             <Copy className="h-4 w-4" />
                           </button>
                         </div>
                       </div>
                       <pre className="whitespace-pre-wrap break-all">
                         {mcpConfig(visibleTokens.has('modal-mcp-config') ? generatedToken : '•'.repeat(32))}
                       </pre>
                    </div>
                    <p className="mt-2 text-xs text-gray-500">
                      Add this configuration to your Cursor MCP settings
                    </p>
                  </div>
                  
                  <div className="flex justify-end space-x-3">
                    <button
                      onClick={() => {
                        setShowTokenModal(false)
                        setGeneratedToken(null)
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