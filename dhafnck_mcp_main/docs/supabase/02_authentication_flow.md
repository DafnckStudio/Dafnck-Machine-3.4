# 🔐 Authentication Flow & Token Management

**Project**: DhafnckMCP Phase 00 MVP  
**Component**: End-to-End Authentication Architecture  
**Created**: 2025-01-27  
**Author**: System Architect Agent  

---

## 📋 **Overview**

This document describes the complete authentication and authorization flow for the DhafnckMCP MVP, from user registration to MCP client access using API tokens.

### **Key Components**
- **Supabase Auth**: User management and session handling
- **Next.js Frontend**: User interface for authentication and token management
- **FastAPI Backend**: MCP server with token validation
- **Cursor MCP Client**: End-user tool using API tokens

---

## 🔄 **Authentication Flow Diagram**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   User      │    │  Next.js    │    │  Supabase   │    │  FastAPI    │
│             │    │  Frontend   │    │    Auth     │    │   Backend   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
        │                   │                   │                   │
        │ 1. Visit App      │                   │                   │
        ├──────────────────▶│                   │                   │
        │                   │ 2. Auth Check    │                   │
        │                   ├──────────────────▶│                   │
        │                   │ 3. Redirect Login │                   │
        │                   │◀──────────────────┤                   │
        │ 4. Login/Signup   │                   │                   │
        ├──────────────────▶│                   │                   │
        │                   │ 5. Authenticate   │                   │
        │                   ├──────────────────▶│                   │
        │                   │ 6. Session Token  │                   │
        │                   │◀──────────────────┤                   │
        │ 7. Dashboard      │                   │                   │
        │◀──────────────────┤                   │                   │
        │ 8. Create Token   │                   │                   │
        ├──────────────────▶│                   │                   │
        │                   │ 9. Store Token    │                   │
        │                   ├──────────────────▶│                   │
        │                   │10. Token Created  │                   │
        │                   │◀──────────────────┤                   │
        │11. Copy Token     │                   │                   │
        │◀──────────────────┤                   │                   │
        │                   │                   │                   │
        │ 12. Configure Cursor with Token       │                   │
        │                   │                   │                   │
        │ 13. MCP Request with Token            │                   │
        ├───────────────────────────────────────────────────────────▶│
        │                   │                   │14. Validate Token │
        │                   │                   │◀──────────────────┤
        │                   │                   │15. Token Valid    │
        │                   │                   ├──────────────────▶│
        │ 16. MCP Response                      │                   │
        │◀───────────────────────────────────────────────────────────┤
```

---

## 🚀 **Phase 1: User Registration & Authentication**

### **1.1 User Registration**
```typescript
// Frontend: User creates account
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'securepassword123',
  options: {
    data: {
      display_name: 'John Doe',
      organization: 'Acme Corp'
    }
  }
})
```

### **1.2 User Login**
```typescript
// Frontend: User logs in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'securepassword123'
})

// Session token is automatically managed by Supabase client
```

### **1.3 Session Management**
```typescript
// Frontend: Check authentication status
const { data: { session } } = await supabase.auth.getSession()

// Listen for auth changes
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'SIGNED_IN') {
    // User is authenticated
    redirectToDashboard()
  } else if (event === 'SIGNED_OUT') {
    // User logged out
    redirectToLogin()
  }
})
```

---

## 🔑 **Phase 2: API Token Management**

### **2.1 Token Creation Flow**
```typescript
// Frontend: User creates new API token
const createApiToken = async (tokenName: string, permissions: object) => {
  // Generate secure random token
  const tokenValue = generateSecureToken(32) // e.g., "dmp_1234567890abcdef..."
  
  // Hash token for storage
  const tokenHash = await hashToken(tokenValue)
  
  // Store in Supabase
  const { data, error } = await supabase.rpc('create_api_token', {
    token_name: tokenName,
    token_hash: tokenHash,
    permissions: permissions,
    expires_at: null // Non-expiring for MVP
  })
  
  if (!error) {
    // Show token to user (only time it's visible)
    displayTokenToUser(tokenValue)
  }
}
```

### **2.2 Token Storage & Security**
```sql
-- Database: Tokens are stored hashed
INSERT INTO api_tokens (user_id, token_name, token_hash, permissions)
VALUES (
  auth.uid(),
  'My Cursor Token',
  'sha256_hash_of_actual_token',
  '{"read": true, "write": true, "admin": false}'
);
```

### **2.3 Token Management Interface**
```typescript
// Frontend: Display user's tokens
const UserTokens = () => {
  const [tokens, setTokens] = useState([])
  
  useEffect(() => {
    const fetchTokens = async () => {
      const { data } = await supabase.rpc('get_user_tokens')
      setTokens(data)
    }
    fetchTokens()
  }, [])
  
  return (
    <div>
      {tokens.map(token => (
        <TokenCard 
          key={token.id}
          name={token.token_name}
          created={token.created_at}
          lastUsed={token.last_used_at}
          onRevoke={() => revokeToken(token.id)}
        />
      ))}
    </div>
  )
}
```

---

## 🛡️ **Phase 3: Token Validation (Backend)**

### **3.1 MCP Server Token Validation**
```python
# FastAPI Backend: Validate incoming tokens
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import hashlib

security = HTTPBearer()

async def validate_api_token(token: str = Depends(security)):
    """Validate API token against Supabase database"""
    
    # Hash the provided token
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Query Supabase for token validation
    result = await supabase.rpc('validate_api_token', {
        'token_hash': token_hash
    }).execute()
    
    if not result.data or not result.data[0]['is_valid']:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired API token"
        )
    
    return {
        'user_id': result.data[0]['user_id'],
        'permissions': result.data[0]['permissions']
    }

# Protected endpoint example
@app.get("/api/v1/projects")
async def get_projects(auth: dict = Depends(validate_api_token)):
    user_id = auth['user_id']
    permissions = auth['permissions']
    
    if not permissions.get('read', False):
        raise HTTPException(403, "Insufficient permissions")
    
    # Return user's projects
    return await get_user_projects(user_id)
```

### **3.2 Token Validation Function (Database)**
```sql
-- Database function for token validation
CREATE OR REPLACE FUNCTION validate_api_token(token_hash TEXT)
RETURNS TABLE (user_id UUID, permissions JSONB, is_valid BOOLEAN)
AS $$
BEGIN
    -- Update last_used_at timestamp
    UPDATE api_tokens 
    SET last_used_at = NOW()
    WHERE api_tokens.token_hash = validate_api_token.token_hash
      AND is_active = true
      AND (expires_at IS NULL OR expires_at > NOW());
    
    -- Return validation result
    RETURN QUERY
    SELECT t.user_id, t.permissions, 
           CASE WHEN t.id IS NOT NULL THEN true ELSE false END
    FROM api_tokens t
    WHERE t.token_hash = validate_api_token.token_hash
      AND t.is_active = true
      AND (t.expires_at IS NULL OR t.expires_at > NOW());
    
    -- Return false if no valid token found
    IF NOT FOUND THEN
        RETURN QUERY SELECT NULL::UUID, NULL::JSONB, false;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## 🖥️ **Phase 4: Cursor MCP Client Integration**

### **4.1 Cursor Configuration**
```json
// .cursor/mcp_servers.json
{
  "dhafnck_mcp": {
    "command": "docker",
    "args": [
      "run", "-it", "--rm",
      "-e", "API_TOKEN=dmp_1234567890abcdef...",
      "dhafnck/mcp-server:latest"
    ]
  }
}
```

### **4.2 MCP Client Request Flow**
```python
# MCP Client: Sending authenticated requests
import httpx

class DhafnckMCPClient:
    def __init__(self, api_token: str, base_url: str):
        self.api_token = api_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    async def create_task(self, task_data: dict):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/tasks",
                json=task_data,
                headers=self.headers
            )
            return response.json()
```

---

## 🔄 **Token Lifecycle Management**

### **5.1 Token Creation**
1. User logs into frontend dashboard
2. Clicks "Create New Token"
3. Provides token name and permissions
4. System generates secure random token
5. Token is hashed and stored in database
6. Plain token shown to user (only once)
7. User copies token for Cursor configuration

### **5.2 Token Usage**
1. Cursor sends MCP request with token
2. Backend receives and hashes token
3. Database validates hashed token
4. Updates `last_used_at` timestamp
5. Returns user context and permissions
6. Request proceeds with user authorization

### **5.3 Token Revocation**
1. User clicks "Revoke" in dashboard
2. Frontend calls revoke function
3. Database sets `is_active = false`
4. Token immediately becomes invalid
5. All future requests with token fail

### **5.4 Token Rotation (Future)**
```typescript
// Future enhancement: Automatic token rotation
const rotateToken = async (tokenId: string) => {
  // Create new token
  const newToken = await createApiToken('Rotated Token', permissions)
  
  // Revoke old token after grace period
  setTimeout(() => {
    revokeToken(tokenId)
  }, ROTATION_GRACE_PERIOD)
  
  return newToken
}
```

---

## 🛡️ **Security Considerations**

### **6.1 Token Security**
- **Storage**: Tokens are hashed using SHA-256 before database storage
- **Transmission**: Always use HTTPS for token transmission
- **Visibility**: Plain tokens shown only once during creation
- **Scope**: Permissions-based access control per token

### **6.2 Authentication Security**
- **Session Management**: Supabase handles secure session tokens
- **Password Policy**: Enforce strong passwords (8+ chars, mixed case, numbers)
- **Rate Limiting**: Limit login attempts and token creation
- **CORS**: Restrict frontend origins

### **6.3 Database Security**
- **RLS**: Row Level Security ensures user data isolation
- **Encryption**: Database encryption at rest
- **Backups**: Regular encrypted backups
- **Audit Logs**: Track all token operations

---

## 📊 **Monitoring & Analytics**

### **7.1 Token Usage Tracking**
```sql
-- Query token usage statistics
SELECT 
    token_name,
    created_at,
    last_used_at,
    CASE 
        WHEN last_used_at > NOW() - INTERVAL '7 days' THEN 'Active'
        WHEN last_used_at IS NULL THEN 'Never Used'
        ELSE 'Inactive'
    END as status
FROM api_tokens 
WHERE user_id = auth.uid() AND is_active = true;
```

### **7.2 Security Monitoring**
- Failed authentication attempts
- Token validation failures
- Suspicious usage patterns
- Account creation monitoring

---

## 🚨 **Error Handling**

### **8.1 Authentication Errors**
```typescript
// Frontend: Handle auth errors gracefully
const handleAuthError = (error: AuthError) => {
  switch (error.code) {
    case 'invalid_credentials':
      showError('Invalid email or password')
      break
    case 'email_not_confirmed':
      showError('Please check your email and confirm your account')
      break
    case 'too_many_requests':
      showError('Too many login attempts. Please try again later.')
      break
    default:
      showError('Authentication failed. Please try again.')
  }
}
```

### **8.2 Token Validation Errors**
```python
# Backend: Handle token errors
class TokenError(Exception):
    pass

class InvalidTokenError(TokenError):
    pass

class ExpiredTokenError(TokenError):
    pass

async def validate_token_with_errors(token: str):
    try:
        return await validate_api_token(token)
    except InvalidTokenError:
        raise HTTPException(401, "Invalid API token")
    except ExpiredTokenError:
        raise HTTPException(401, "API token has expired")
    except Exception:
        raise HTTPException(500, "Token validation failed")
```

---

## ✅ **Testing Strategy**

### **9.1 Authentication Testing**
```typescript
// Test user registration and login
describe('Authentication', () => {
  test('user can register with valid email', async () => {
    const result = await supabase.auth.signUp({
      email: 'test@example.com',
      password: 'password123'
    })
    expect(result.error).toBeNull()
    expect(result.data.user).toBeDefined()
  })
  
  test('user can login with correct credentials', async () => {
    const result = await supabase.auth.signInWithPassword({
      email: 'test@example.com',
      password: 'password123'
    })
    expect(result.error).toBeNull()
    expect(result.data.session).toBeDefined()
  })
})
```

### **9.2 Token Management Testing**
```python
# Test token validation
import pytest

@pytest.mark.asyncio
async def test_valid_token():
    token = "valid_test_token"
    result = await validate_api_token(token)
    assert result['is_valid'] == True
    assert result['user_id'] is not None

@pytest.mark.asyncio
async def test_invalid_token():
    token = "invalid_test_token"
    with pytest.raises(HTTPException) as exc:
        await validate_api_token(token)
    assert exc.value.status_code == 401
```

---

## 📚 **Integration Examples**

### **10.1 Complete Frontend Integration**
```typescript
// Complete authentication component
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export const AuthProvider = ({ children }) => {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setLoading(false)
    })
    
    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setSession(session)
        setLoading(false)
      }
    )
    
    return () => subscription.unsubscribe()
  }, [])
  
  return (
    <AuthContext.Provider value={{ session, loading }}>
      {children}
    </AuthContext.Provider>
  )
}
```

### **10.2 Complete Backend Integration**
```python
# Complete FastAPI integration
from fastapi import FastAPI, Depends, HTTPException
from supabase import create_client

app = FastAPI()
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Skip auth for health check and public endpoints
    if request.url.path in ["/health", "/docs"]:
        return await call_next(request)
    
    # Extract and validate token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid authorization header")
    
    token = auth_header.split(" ")[1]
    user_context = await validate_api_token(token)
    
    # Add user context to request state
    request.state.user = user_context
    
    return await call_next(request)

@app.get("/api/v1/tasks")
async def get_tasks(request: Request):
    user_id = request.state.user['user_id']
    permissions = request.state.user['permissions']
    
    if not permissions.get('read'):
        raise HTTPException(403, "Read permission required")
    
    return await get_user_tasks(user_id)
```

---

**Next Steps:**
1. Implement frontend authentication components
2. Build backend token validation system
3. Create comprehensive test suite
4. Set up monitoring and logging
5. Deploy and test end-to-end flow

**Related Documents:**
- [Supabase Setup Guide](./01_supabase_setup_guide.md)
- [Environment Configuration](./config/environment_template.env)
- [Database Schema](./migrations/001_initial_schema.sql) 