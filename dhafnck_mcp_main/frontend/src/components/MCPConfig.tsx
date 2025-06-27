'use client'

import { Copy, ExternalLink, Eye, EyeOff, Key } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'react-hot-toast'

interface MCPConfigProps {
  token: string
  className?: string
  showInstructions?: boolean
  title?: string
}

export default function MCPConfig({ 
  token, 
  className = '', 
  showInstructions = true,
  title = 'MCP Configuration'
}: MCPConfigProps) {
  const [showToken, setShowToken] = useState(false)
  
  const mcpConfig = `{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "DHAFNCK_TOKEN=${showToken ? token : '•'.repeat(32)}",
        "-v", "dhafnck-data:/data",
        "dhafnck/mcp-server:latest"
      ],
      "env": {
        "DHAFNCK_TOKEN": "${showToken ? token : '•'.repeat(32)}"
      }
    }
  }
}`

  const mcpConfigWithRealToken = `{
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

  const handleCopyConfig = async () => {
    try {
      await navigator.clipboard.writeText(mcpConfigWithRealToken)
      toast.success('MCP configuration copied to clipboard!')
    } catch (error) {
      toast.error('Failed to copy configuration')
    }
  }

  const toggleTokenVisibility = () => {
    setShowToken(!showToken)
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border ${className}`}>
      <div className="p-6 border-b">
        <div className="flex items-center">
          <Key className="h-5 w-5 text-gray-400 mr-2" />
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
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
                  onClick={toggleTokenVisibility}
                  className="text-gray-400 hover:text-white transition-colors"
                  title={showToken ? 'Hide token' : 'Show token'}
                >
                  {showToken ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
                <button
                  onClick={handleCopyConfig}
                  className="text-gray-400 hover:text-white transition-colors"
                  title="Copy configuration"
                >
                  <Copy className="h-4 w-4" />
                </button>
              </div>
            </div>
            <pre className="whitespace-pre-wrap break-all text-xs">
              {mcpConfig}
            </pre>
          </div>
        </div>
        
        {showInstructions && (
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
            <div className="mt-3 pt-3 border-t border-blue-200">
              <p className="text-sm text-blue-800 mb-2">
                <strong>Available MCP Tools:</strong>
              </p>
              <div className="grid grid-cols-2 gap-1 text-xs text-blue-700">
                <span>• manage_project</span>
                <span>• manage_task</span>
                <span>• manage_subtask</span>
                <span>• manage_agent</span>
                <span>• call_agent</span>
                <span>• update_auto_rule</span>
                <span>• validate_rules</span>
                <span>• manage_cursor_rules</span>
                <span>• regenerate_auto_rule</span>
                <span>• validate_tasks_json</span>
              </div>
            </div>
          </div>
        )}
        
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <h5 className="font-medium text-gray-900 mb-2">Need Help?</h5>
          <div className="flex items-center space-x-4 text-sm">
            <a
              href="https://github.com/dhafnck/dhafnck_mcp/blob/main/docs/CURSOR_SETUP.md"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 flex items-center"
            >
              <ExternalLink className="h-3 w-3 mr-1" />
              Setup Guide
            </a>
            <a
              href="https://github.com/dhafnck/dhafnck_mcp/issues"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 flex items-center"
            >
              <ExternalLink className="h-3 w-3 mr-1" />
              Get Support
            </a>
          </div>
        </div>
      </div>
    </div>
  )
} 