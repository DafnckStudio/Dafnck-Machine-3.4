-- Migration: 001_initial_schema.sql
-- Description: Create initial database schema for DhafnckMCP MVP
-- Created: 2025-01-27
-- Author: System Architect Agent

-- =============================================================================
-- API TOKENS TABLE
-- =============================================================================

-- Create api_tokens table for storing user API tokens
CREATE TABLE IF NOT EXISTS public.api_tokens (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    token_name TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    permissions JSONB DEFAULT '{"read": true, "write": true}',
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    
    -- Constraints
    CONSTRAINT token_name_length CHECK (char_length(token_name) >= 1 AND char_length(token_name) <= 100),
    CONSTRAINT valid_expiry CHECK (expires_at IS NULL OR expires_at > created_at)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_api_tokens_user_id ON public.api_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_api_tokens_hash ON public.api_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_api_tokens_active ON public.api_tokens(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_api_tokens_expires ON public.api_tokens(expires_at) WHERE expires_at IS NOT NULL;

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
-- DATABASE FUNCTIONS
-- =============================================================================

-- Function to validate API tokens (called by MCP server)
CREATE OR REPLACE FUNCTION public.validate_api_token(token_hash TEXT)
RETURNS TABLE (
    user_id UUID,
    permissions JSONB,
    is_valid BOOLEAN
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Update last_used_at and return token info
    UPDATE public.api_tokens 
    SET last_used_at = NOW()
    WHERE api_tokens.token_hash = validate_api_token.token_hash
      AND is_active = true
      AND (expires_at IS NULL OR expires_at > NOW());
    
    RETURN QUERY
    SELECT 
        t.user_id,
        t.permissions,
        CASE 
            WHEN t.id IS NOT NULL THEN true 
            ELSE false 
        END as is_valid
    FROM public.api_tokens t
    WHERE t.token_hash = validate_api_token.token_hash
      AND t.is_active = true
      AND (t.expires_at IS NULL OR t.expires_at > NOW());
    
    -- If no valid token found, return invalid result
    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::UUID, NULL::JSONB, false;
    END IF;
END;
$$;

-- Function to create API token
CREATE OR REPLACE FUNCTION public.create_api_token(
    token_name TEXT,
    token_hash TEXT,
    permissions JSONB DEFAULT '{"read": true, "write": true}',
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    new_token_id UUID;
BEGIN
    INSERT INTO public.api_tokens (user_id, token_name, token_hash, permissions, expires_at)
    VALUES (auth.uid(), token_name, token_hash, permissions, expires_at)
    RETURNING id INTO new_token_id;
    
    RETURN new_token_id;
END;
$$;

-- Function to revoke API token
CREATE OR REPLACE FUNCTION public.revoke_api_token(token_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE public.api_tokens 
    SET is_active = false 
    WHERE id = token_id AND user_id = auth.uid();
    
    RETURN FOUND;
END;
$$;

-- Function to get user's active tokens
CREATE OR REPLACE FUNCTION public.get_user_tokens()
RETURNS TABLE (
    id UUID,
    token_name TEXT,
    permissions JSONB,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id,
        t.token_name,
        t.permissions,
        t.expires_at,
        t.created_at,
        t.last_used_at
    FROM public.api_tokens t
    WHERE t.user_id = auth.uid()
      AND t.is_active = true
    ORDER BY t.created_at DESC;
END;
$$;

-- Function to update token last used timestamp
CREATE OR REPLACE FUNCTION public.update_token_usage(token_hash TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE public.api_tokens 
    SET last_used_at = NOW()
    WHERE api_tokens.token_hash = update_token_usage.token_hash
      AND is_active = true;
    
    RETURN FOUND;
END;
$$;

-- =============================================================================
-- COMMENTS AND DOCUMENTATION
-- =============================================================================

-- Add table comments
COMMENT ON TABLE public.api_tokens IS 'Stores API tokens for user authentication with MCP clients';
COMMENT ON TABLE public.user_profiles IS 'Extended user profile information';

-- Add column comments
COMMENT ON COLUMN public.api_tokens.token_hash IS 'Hashed version of the API token for security';
COMMENT ON COLUMN public.api_tokens.permissions IS 'JSON object defining token permissions and scopes';
COMMENT ON COLUMN public.api_tokens.expires_at IS 'Token expiration timestamp, NULL for non-expiring tokens';
COMMENT ON COLUMN public.api_tokens.last_used_at IS 'Timestamp of last token usage for monitoring';

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

-- Grant necessary permissions for authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON public.api_tokens TO authenticated;
GRANT ALL ON public.user_profiles TO authenticated;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION public.validate_api_token(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.create_api_token(TEXT, TEXT, JSONB, TIMESTAMP WITH TIME ZONE) TO authenticated;
GRANT EXECUTE ON FUNCTION public.revoke_api_token(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_user_tokens() TO authenticated;
GRANT EXECUTE ON FUNCTION public.update_token_usage(TEXT) TO authenticated;

-- Grant service role permissions for token validation
GRANT EXECUTE ON FUNCTION public.validate_api_token(TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION public.update_token_usage(TEXT) TO service_role;

-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================

-- Insert migration record (if you're tracking migrations)
-- INSERT INTO public.migrations (name, executed_at) VALUES ('001_initial_schema', NOW());

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Migration 001_initial_schema completed successfully';
    RAISE NOTICE 'Created tables: api_tokens, user_profiles';
    RAISE NOTICE 'Created functions: validate_api_token, create_api_token, revoke_api_token, get_user_tokens, update_token_usage';
    RAISE NOTICE 'Enabled RLS with user-scoped policies';
END $$; 