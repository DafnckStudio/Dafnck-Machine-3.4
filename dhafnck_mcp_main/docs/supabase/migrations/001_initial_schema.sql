-- Migration: 001_initial_schema.sql
-- Description: Create initial database schema for DhafnckMCP MVP
-- Created: 2025-01-27
-- Updated: 2025-01-27 (Fixed column names to match frontend)
-- Author: System Architect Agent

-- =============================================================================
-- API TOKENS TABLE
-- =============================================================================

-- Create api_tokens table with frontend-compatible column names
CREATE TABLE IF NOT EXISTS public.api_tokens (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,                      -- Frontend expects 'name' not 'token_name'
    token TEXT NOT NULL UNIQUE,              -- Frontend expects 'token' not 'token_hash'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE,     -- Frontend expects 'last_used' not 'last_used_at'
    is_active BOOLEAN DEFAULT true,
    
    -- Constraints
    CONSTRAINT token_name_length CHECK (char_length(name) >= 1 AND char_length(name) <= 100)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_api_tokens_user_id ON public.api_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_api_tokens_token ON public.api_tokens(token);
CREATE INDEX IF NOT EXISTS idx_api_tokens_active ON public.api_tokens(is_active) WHERE is_active = true;

-- =============================================================================
-- USER PROFILES TABLE (Optional for MVP)
-- =============================================================================

-- Create user_profiles table for extended user information
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL UNIQUE,
    display_name TEXT,
    organization TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON public.user_profiles(user_id);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS on api_tokens table
ALTER TABLE public.api_tokens ENABLE ROW LEVEL SECURITY;

-- Enable RLS on user_profiles table
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- RLS POLICIES FOR API_TOKENS
-- =============================================================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own tokens" ON public.api_tokens;
DROP POLICY IF EXISTS "Users can create own tokens" ON public.api_tokens;
DROP POLICY IF EXISTS "Users can update own tokens" ON public.api_tokens;
DROP POLICY IF EXISTS "Users can delete own tokens" ON public.api_tokens;

-- Users can only see their own tokens
CREATE POLICY "Users can view own tokens" ON public.api_tokens
    FOR SELECT USING (auth.uid() = user_id);

-- Users can create tokens for themselves
CREATE POLICY "Users can create own tokens" ON public.api_tokens
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own tokens
CREATE POLICY "Users can update own tokens" ON public.api_tokens
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own tokens
CREATE POLICY "Users can delete own tokens" ON public.api_tokens
    FOR DELETE USING (auth.uid() = user_id);

-- =============================================================================
-- RLS POLICIES FOR USER_PROFILES
-- =============================================================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can create own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;

-- Users can view their own profile
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = user_id);

-- Users can create their own profile
CREATE POLICY "Users can create own profile" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

-- =============================================================================
-- DATABASE FUNCTIONS (Updated for new column names)
-- =============================================================================

-- Function to validate API tokens (called by MCP server)
CREATE OR REPLACE FUNCTION public.validate_api_token(token_value TEXT)
RETURNS TABLE (
    user_id UUID,
    is_valid BOOLEAN
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Update last_used and return token info
    UPDATE public.api_tokens 
    SET last_used = NOW()
    WHERE api_tokens.token = validate_api_token.token_value
      AND is_active = true;
    
    RETURN QUERY
    SELECT 
        t.user_id,
        CASE 
            WHEN t.id IS NOT NULL THEN true 
            ELSE false 
        END as is_valid
    FROM public.api_tokens t
    WHERE t.token = validate_api_token.token_value
      AND t.is_active = true;
    
    -- If no valid token found, return invalid result
    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::UUID, false;
    END IF;
END;
$$;

-- Function to update token last used timestamp
CREATE OR REPLACE FUNCTION public.update_token_usage(token_value TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE public.api_tokens 
    SET last_used = NOW()
    WHERE api_tokens.token = update_token_usage.token_value
      AND is_active = true;
    
    RETURN FOUND;
END;
$$;

-- =============================================================================
-- COMMENTS AND DOCUMENTATION
-- =============================================================================

-- Add table comments
COMMENT ON TABLE public.api_tokens IS 'API tokens for user authentication - MVP schema matching frontend';
COMMENT ON TABLE public.user_profiles IS 'Extended user profile information';

-- Add column comments
COMMENT ON COLUMN public.api_tokens.token IS 'Actual API token value (stored as plaintext for MVP)';
COMMENT ON COLUMN public.api_tokens.name IS 'User-friendly name for the token';
COMMENT ON COLUMN public.api_tokens.last_used IS 'Timestamp of last token usage for monitoring';

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

-- Grant necessary permissions for authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON public.api_tokens TO authenticated;
GRANT ALL ON public.user_profiles TO authenticated;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION public.validate_api_token(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.update_token_usage(TEXT) TO authenticated;

-- Grant service role permissions for token validation
GRANT EXECUTE ON FUNCTION public.validate_api_token(TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION public.update_token_usage(TEXT) TO service_role;

-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Migration 001_initial_schema completed successfully';
    RAISE NOTICE 'Created tables: api_tokens (frontend-compatible), user_profiles';
    RAISE NOTICE 'Created functions: validate_api_token, update_token_usage';
    RAISE NOTICE 'Enabled RLS with user-scoped policies';
    RAISE NOTICE 'Schema now matches frontend expectations: name, token, last_used';
END $$; 