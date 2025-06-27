# 🚀 Supabase Project Configuration Guide

**Project**: DhafnckMCP Phase 00 MVP  
**Component**: Authentication & Token Management  
**Estimated Time**: 2 hours  
**Prerequisites**: Supabase account, admin access  

---

## 📋 **Overview**

This guide sets up Supabase as the authentication and token management backend for the DhafnckMCP MVP. Users will authenticate via the Next.js frontend and generate API tokens for Cursor MCP client access.

### **Architecture Components**
- **Supabase Auth**: User registration, login, session management
- **Custom Tables**: API token storage and management
- **Row Level Security**: User-scoped data access
- **API Functions**: Token validation and management endpoints

---

## 🎯 **Step 1: Create Supabase Project**

### **1.1 Project Creation**
1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Click "New Project"
3. **Organization**: Select or create organization
4. **Project Name**: `dhafnck-mcp-mvp`
5. **Database Password**: Generate strong password (save securely)
6. **Region**: Choose closest to your users (e.g., `us-east-1`)
7. Click "Create new project"

### **1.2 Project Configuration**
- **Project URL**: `https://[project-id].supabase.co`
- **API Keys**: Note down `anon` and `service_role` keys
- **Database URL**: Available in Settings > Database

---

## 🔐 **Step 2: Authentication Configuration**

### **2.1 Enable Authentication Providers**
1. Go to **Authentication > Providers**
2. **Email**: Enable (default)
3. **Additional Providers** (optional for MVP):
   - GitHub OAuth (recommended for developers)
   - Google OAuth (for broader user base)

### **2.2 Authentication Settings**
1. Go to **Authentication > Settings**
2. **Site URL**: `http://localhost:3000` (for development)
3. **Redirect URLs**: 
   - `http://localhost:3000/auth/callback`
   - `https://your-domain.com/auth/callback` (for production)
4. **Email Settings**:
   - **Enable email confirmations**: `false` (for MVP speed)
   - **Enable secure email change**: `true`
5. **Session Settings**:
   - **JWT expiry**: `86400` (24 hours)
   - **Refresh token rotation**: `true`

### **2.3 Email Templates (Optional)**
Customize welcome and confirmation emails in **Authentication > Email Templates**

---

## 🗄️ **Step 3: Database Schema Setup**

### **3.1 Create API Tokens Table**
```sql
-- Create api_tokens table
CREATE TABLE public.api_tokens (
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
CREATE INDEX idx_api_tokens_user_id ON public.api_tokens(user_id);
CREATE INDEX idx_api_tokens_hash ON public.api_tokens(token_hash);
CREATE INDEX idx_api_tokens_active ON public.api_tokens(is_active) WHERE is_active = true;
```

### **3.2 Create User Profiles Table (Optional)**
```sql
-- Create user_profiles table
CREATE TABLE public.user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL UNIQUE,
    display_name TEXT,
    organization TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index
CREATE INDEX idx_user_profiles_user_id ON public.user_profiles(user_id);
```

---

## 🔒 **Step 4: Row Level Security (RLS)**

### **4.1 Enable RLS**
```sql
-- Enable RLS on api_tokens table
ALTER TABLE public.api_tokens ENABLE ROW LEVEL SECURITY;

-- Enable RLS on user_profiles table
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
```

### **4.2 Create RLS Policies**
```sql
-- API Tokens Policies
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

-- User Profiles Policies
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own profile" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = user_id);
```

---

## ⚙️ **Step 5: Database Functions**

### **5.1 Token Validation Function**
```sql
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
```

### **5.2 Token Management Functions**
```sql
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
```

---

## 🔑 **Step 6: Environment Variables**

### **6.1 Copy Configuration Values**
Go to **Settings > API** and copy:

```bash
# Supabase Configuration
SUPABASE_URL=https://[your-project-id].supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database Configuration (from Settings > Database)
DATABASE_URL=postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres

# JWT Configuration
JWT_SECRET=[your-jwt-secret]
```

### **6.2 Environment Files**
Create `.env.local` for Next.js frontend:
```bash
NEXT_PUBLIC_SUPABASE_URL=https://[your-project-id].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Create `.env` for FastAPI backend:
```bash
SUPABASE_URL=https://[your-project-id].supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
JWT_SECRET=[your-jwt-secret]
```

---

## ✅ **Step 7: Testing & Validation**

### **7.1 Test Authentication**
1. Create test user via Supabase dashboard
2. Verify user appears in **Authentication > Users**
3. Test login/logout flow

### **7.2 Test Token Operations**
```sql
-- Test token creation
SELECT public.create_api_token('Test Token', 'test_hash_123', '{"read": true}');

-- Test token validation
SELECT * FROM public.validate_api_token('test_hash_123');

-- Test token listing
SELECT * FROM public.api_tokens WHERE user_id = auth.uid();
```

### **7.3 Verify RLS Policies**
1. Create second test user
2. Verify users can only see their own tokens
3. Test token operations across users

---

## 📚 **Step 8: Documentation**

### **8.1 API Endpoints Summary**
- **Authentication**: Built-in Supabase auth endpoints
- **Token Management**: Custom functions via PostgREST
- **User Profiles**: Standard CRUD via PostgREST

### **8.2 Integration Points**
- **Frontend**: Supabase client for auth and token management
- **Backend**: Service role key for token validation
- **MCP Client**: API tokens for authentication

### **8.3 Security Considerations**
- All tokens are hashed before storage
- RLS ensures user data isolation
- Service role key only used for token validation
- Regular token rotation recommended

---

## 🚨 **Troubleshooting**

### **Common Issues**
1. **RLS blocking access**: Check policy conditions
2. **Token validation failing**: Verify service role key
3. **CORS issues**: Check site URL configuration
4. **Email not sending**: Configure SMTP settings

### **Support Resources**
- [Supabase Documentation](https://supabase.com/docs)
- [Authentication Guide](https://supabase.com/docs/guides/auth)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)

---

**Completion Checklist:**
- [ ] Supabase project created and configured
- [ ] Database schema deployed
- [ ] RLS policies active
- [ ] Functions tested
- [ ] Environment variables documented
- [ ] Authentication flow validated
- [ ] Ready for frontend integration

**Next Steps:**
- Integrate with Next.js frontend
- Implement backend token validation
- Create user dashboard for token management 