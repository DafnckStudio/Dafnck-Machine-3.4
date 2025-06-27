'use client'

import { useAuth } from '@/contexts/AuthContext'
import { ApiToken, supabase } from '@/lib/supabase'
import { generateSecureToken, generateUUID } from '@/lib/utils'
import { useEffect, useState } from 'react'

export function useTokens() {
  const { user } = useAuth()
  const [tokens, setTokens] = useState<ApiToken[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTokens = async () => {
    if (!user) {
      setTokens([])
      setLoading(false)
      return
    }

    try {
      const { data, error } = await supabase
        .from('api_tokens')
        .select('*')
        .eq('user_id', user.id)
        .eq('is_active', true)
        .order('created_at', { ascending: false })

      if (error) throw error
      setTokens(data || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tokens')
    } finally {
      setLoading(false)
    }
  }

  const generateToken = async (name: string) => {
    if (!user) throw new Error('User not authenticated')

    try {
      const token = generateSecureToken()
      const { data, error } = await supabase
        .from('api_tokens')
        .insert({
          id: generateUUID(),
          user_id: user.id,
          token,
          name,
          is_active: true
        })
        .select()
        .single()

      if (error) throw error
      
      await fetchTokens() // Refresh the list
      return { token: data.token, error: null }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate token'
      setError(errorMessage)
      return { token: null, error: errorMessage }
    }
  }

  const revokeToken = async (tokenId: string) => {
    if (!user) throw new Error('User not authenticated')

    try {
      const { error } = await supabase
        .from('api_tokens')
        .update({ is_active: false })
        .eq('id', tokenId)
        .eq('user_id', user.id)

      if (error) throw error
      
      await fetchTokens() // Refresh the list
      return { error: null }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to revoke token'
      setError(errorMessage)
      return { error: errorMessage }
    }
  }

  const updateLastUsed = async (tokenId: string) => {
    if (!user) return

    try {
      await supabase
        .from('api_tokens')
        .update({ last_used: new Date().toISOString() })
        .eq('id', tokenId)
        .eq('user_id', user.id)
    } catch (err) {
      // Silently fail for last_used updates
      console.warn('Failed to update last_used:', err)
    }
  }

  useEffect(() => {
    fetchTokens()
  }, [user])

  return {
    tokens,
    loading,
    error,
    generateToken,
    revokeToken,
    updateLastUsed,
    refreshTokens: fetchTokens
  }
} 