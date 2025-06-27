'use client'

import { Apple, Box, Brain, Copy, ExternalLink, Eye, EyeOff, Key, Monitor } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'react-hot-toast'

type EnvironmentType = 'wsl' | 'linux-macos' | 'docker'

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
  const [environment, setEnvironment] = useState<EnvironmentType>('docker')
  const [includeSequentialThinking, setIncludeSequentialThinking] = useState(true)
  
  const getEnvironmentConfig = (env: EnvironmentType, hideToken: boolean = false) => {
    const displayToken = hideToken ? '•'.repeat(32) : token
    const username = '<username>' // Placeholder for username
    
    const baseConfig = {
      wsl: {
        dhafnck_mcp: {
          command: "wsl.exe",
          args: [
            "--cd", `/home/${username}/agentic-project`,
            "--exec", `/home/${username}/agentic-project/dhafnck_mcp_main/.venv/bin/python`,
            "-m", "fastmcp.server.mcp_entry_point"
          ],
          env: {
            PYTHONPATH: "dhafnck_mcp_main/src",
            TASKS_JSON_PATH: ".cursor/rules/tasks/tasks.json",
            TASK_JSON_BACKUP_PATH: ".cursor/rules/tasks/backup",
            MCP_TOOL_CONFIG: ".cursor/tool_config.json",
            AGENTS_OUTPUT_DIR: ".cursor/rules/agents",
            AUTO_RULE_PATH: ".cursor/rules/auto_rule.mdc",
            BRAIN_DIR_PATH: ".cursor/rules/brain",
            PROJECTS_FILE_PATH: ".cursor/rules/brain/projects.json",
            PROJECT_ROOT_PATH: ".",
            CURSOR_AGENT_DIR_PATH: "dhafnck_mcp_main/yaml-lib",
            AGENT_YAML_LIB_PATH: "dhafnck_mcp_main/yaml-lib",
            DHAFNCK_TOKEN: displayToken
          },
          transport: "stdio",
          debug: true
        }
      },
      'linux-macos': {
        dhafnck_mcp: {
          command: `/home/${username}/agentic-project/dhafnck_mcp_main/.venv/bin/python`,
          args: [
            "-m",
            "fastmcp.server.mcp_entry_point"
          ],
          cwd: `/home/${username}/agentic-project`,
          env: {
            PYTHONPATH: "dhafnck_mcp_main/src",
            TASKS_JSON_PATH: ".cursor/rules/tasks/tasks.json",
            TASK_JSON_BACKUP_PATH: ".cursor/rules/tasks/backup",
            MCP_TOOL_CONFIG: ".cursor/tool_config.json",
            AGENTS_OUTPUT_DIR: ".cursor/rules/agents",
            AUTO_RULE_PATH: ".cursor/rules/auto_rule.mdc",
            BRAIN_DIR_PATH: ".cursor/rules/brain",
            PROJECTS_FILE_PATH: ".cursor/rules/brain/projects.json",
            PROJECT_ROOT_PATH: ".",
            CURSOR_AGENT_DIR_PATH: "dhafnck_mcp_main/yaml-lib",
            AGENT_YAML_LIB_PATH: "dhafnck_mcp_main/yaml-lib",
            DHAFNCK_TOKEN: displayToken
          },
          transport: "stdio",
          debug: true
        }
      },
      docker: {        
        dhafnck_mcp_http: {
          url: "http://localhost:8000/mcp/",
          headers: {
            Authorization: `Bearer ${displayToken}`
          },
          transport: "http"
        }
      }
    }

    const sequentialThinkingConfig = {
      "sequential-thinking": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ],
      "env": {}
    },
    }

    const selectedConfig = baseConfig[env]
    const mcpServers = includeSequentialThinking 
      ? { ...selectedConfig, ...sequentialThinkingConfig }
      : selectedConfig

    return JSON.stringify({ mcpServers }, null, 2)
  }

  const getEnvironmentInstructions = (env: EnvironmentType) => {
    const username = '<username>' // Placeholder
    
    switch (env) {
      case 'docker':
        return {
          setup: [
            'Install Docker Desktop and ensure it\'s running',
            'Pull the DhafnckMCP Docker image: docker pull dhafnck/mcp-server:latest',
            'Copy the configuration above',
            'Open Cursor settings (Cmd/Ctrl + ,)',
            'Search for "MCP" or navigate to Extensions → MCP',
            'Add the configuration to your mcp.json file',
            'Restart Cursor to load the MCP server'
          ],
          requirements: 'Docker Desktop must be installed and running',
          notes: 'Docker setup is the simplest and most reliable option.'
        }
      
      case 'wsl':
        return {
          setup: [
            `Replace ${username} with your actual Windows username`,
            'Ensure WSL2 is installed and running',
            'Navigate to /home/<username>/agentic-project in WSL',
            'Activate the virtual environment: source dhafnck_mcp_main/.venv/bin/activate',
            'Install dependencies: pip install -e dhafnck_mcp_main/',
            'Copy the configuration above',
            'Open Cursor settings (Cmd/Ctrl + ,)',
            'Search for "MCP" or navigate to Extensions → MCP',
            'Add the configuration to your mcp.json file',
            'Restart Cursor to load the MCP server'
          ],
          requirements: 'WSL2 with Python 3.10+ and virtual environment setup',
          notes: 'This configuration runs the MCP server directly in WSL from Windows Cursor.'
        }
      
      case 'linux-macos':
        return {
          setup: [
            `Replace ${username} with your actual username`,
            'Ensure Python 3.10+ is installed',
            'Navigate to /home/<username>/agentic-project (or equivalent on macOS)',
            'Activate the virtual environment: source dhafnck_mcp_main/.venv/bin/activate',
            'Install dependencies: pip install -e dhafnck_mcp_main/',
            'Copy the configuration above',
            'Open Cursor settings (Cmd/Ctrl + ,)',
            'Search for "MCP" or navigate to Extensions → MCP',
            'Add the configuration to your mcp.json file',
            'Restart Cursor to load the MCP server'
          ],
          requirements: 'Linux/macOS with Python 3.10+ and virtual environment setup',
          notes: 'This configuration runs the MCP server natively on Linux or macOS.'
        }
      
      default:
        return { setup: [], requirements: '', notes: '' }
    }
  }

  const mcpConfig = getEnvironmentConfig(environment, !showToken)
  const mcpConfigWithRealToken = getEnvironmentConfig(environment, false)

  const handleCopyConfig = async () => {
    try {
      await navigator.clipboard.writeText(mcpConfigWithRealToken)
      toast.success('MCP configuration copied to clipboard!')
    } catch {
      toast.error('Failed to copy configuration')
    }
  }

  const toggleTokenVisibility = () => {
    setShowToken(!showToken)
  }

  const environmentOptions = [
    { 
      id: 'docker' as EnvironmentType, 
      label: 'Docker', 
      icon: Box,
      description: 'Run in Docker container (recommended)' 
    },
    { 
      id: 'wsl' as EnvironmentType, 
      label: 'WSL (Windows)', 
      icon: Monitor,
      description: 'Run in WSL2 from Windows Cursor' 
    },
    { 
      id: 'linux-macos' as EnvironmentType, 
      label: 'Linux/macOS', 
      icon: Apple,
      description: 'Run natively on Linux or macOS' 
    }
  ]

  const currentInstructions = getEnvironmentInstructions(environment)

  return (
    <div className={`bg-white rounded-lg shadow-sm border ${className}`}>
      <div className="p-6 border-b">
        <div className="flex items-center">
          <Key className="h-5 w-5 text-gray-400 mr-2" />
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        </div>
        <p className="mt-1 text-sm text-gray-600">
          Choose your environment and add the configuration to Cursor
        </p>
      </div>
      
      <div className="p-6">
        {/* Environment Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Select your environment:
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {environmentOptions.map((option) => {
              const IconComponent = option.icon
              return (
                <label
                  key={option.id}
                  className={`relative flex cursor-pointer rounded-lg border p-4 focus:outline-none transition-colors ${
                    environment === option.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 bg-white hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="radio"
                    name="environment"
                    value={option.id}
                    checked={environment === option.id}
                    onChange={(e) => setEnvironment(e.target.value as EnvironmentType)}
                    className="sr-only"
                  />
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <IconComponent className={`h-5 w-5 ${
                        environment === option.id ? 'text-blue-600' : 'text-gray-400'
                      }`} />
                    </div>
                    <div className="ml-3">
                      <div className={`text-sm font-medium ${
                        environment === option.id ? 'text-blue-900' : 'text-gray-900'
                      }`}>
                        {option.label}
                      </div>
                      <div className={`text-xs ${
                        environment === option.id ? 'text-blue-700' : 'text-gray-500'
                      }`}>
                        {option.description}
                      </div>
                    </div>
                  </div>
                </label>
              )
            })}
          </div>
        </div>

        {/* Sequential Thinking Option */}
        <div className="mb-6">
          <div className="flex items-center justify-between p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="flex items-center">
              <Brain className="h-5 w-5 text-purple-600 mr-3" />
              <div>
                <h4 className="text-sm font-medium text-purple-900">Include Sequential Thinking MCP</h4>
                <p className="text-xs text-purple-700 mt-1">
                  Recommended for complex problem-solving and multi-step reasoning tasks
                </p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={includeSequentialThinking}
                onChange={(e) => setIncludeSequentialThinking(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>
        </div>

        {/* Configuration Display */}
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
            <div className="mb-3">
              <p className="text-sm text-blue-800 font-medium">Requirements:</p>
              <p className="text-sm text-blue-700">{currentInstructions.requirements}</p>
            </div>
            <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800">
              {currentInstructions.setup.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ol>
            {currentInstructions.notes && (
              <div className="mt-3 pt-3 border-t border-blue-200">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> {currentInstructions.notes}
                </p>
              </div>
            )}
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
              {includeSequentialThinking && (
                <div className="mt-2 pt-2 border-t border-blue-300">
                  <p className="text-sm text-blue-800 mb-1">
                    <strong>Sequential Thinking Tools:</strong>
                  </p>
                  <div className="text-xs text-blue-700">
                    <span>• sequentialthinking (for complex problem-solving)</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <h5 className="font-medium text-gray-900 mb-2">Need Help?</h5>
          <div className="flex items-center space-x-4 text-sm">
            <a
              href="https://github.com/dhafnck/dhafnck_mcp/blob/main/CURSOR_MCP_SETUP.md"
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