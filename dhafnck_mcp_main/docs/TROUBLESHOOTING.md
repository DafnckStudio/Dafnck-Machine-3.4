# DhafnckMCP Troubleshooting Guide

## 🚨 "Failed to generate token" Error

### Problem Description
You're seeing a "Failed to generate token" error even though a valid token object is being generated. This indicates a database schema mismatch between the frontend expectations and the actual Supabase database structure.

### Root Cause
**Database Schema Mismatch**: The frontend code expects different column names than what's defined in the original database migration.

**Frontend expects:**
- `name` (token name)
- `token` (actual token value)  
- `last_used` (last usage timestamp)

**Original database schema had:**
- `token_name` (instead of `name`)
- `token_hash` (instead of `token`)
- `last_used_at` (instead of `last_used`)

### 🔧 Solution Steps

#### Step 1: Set Up Your Supabase Project (if not done)
1. Go to [Supabase](https://supabase.com) and create a new project
2. Get your project URL and anon key from Settings > API
3. Update your `.env.local` file:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
   ```

#### Step 2: Run the Corrected Database Migration
1. **Go to your Supabase dashboard** → **SQL Editor**
2. **Copy and paste** the contents of `docs/supabase/migrations/001_initial_schema.sql`
3. **Click "Run"** to execute the migration
4. **Verify** the table was created with the correct schema

#### Step 3: Verify the Fix
1. **Restart your Next.js development server**:
   ```bash
   cd dhafnck_mcp_main/frontend
   npm run dev
   ```
2. **Try generating a token again**
3. **Check the Supabase dashboard** → **Table Editor** → **api_tokens** to see if the token was saved

### 🔍 How to Verify It's Working

#### Check Database Schema
In Supabase dashboard → Table Editor → api_tokens, you should see these columns:
- `id` (UUID)
- `user_id` (UUID) 
- `name` (TEXT)
- `token` (TEXT)
- `created_at` (TIMESTAMP)
- `last_used` (TIMESTAMP)
- `is_active` (BOOLEAN)

#### Check Frontend Console
Open browser developer tools → Console. You should see:
- No errors when generating tokens
- Successful API responses
- Token data displaying correctly in the UI

### 🛠️ Alternative Quick Fix (If Migration Doesn't Work)

If you can't run the migration, you can manually create the table:

1. **Go to Supabase dashboard** → **Table Editor**
2. **Create new table** named `api_tokens`
3. **Add these columns**:
   - `id`: uuid, primary key, default: gen_random_uuid()
   - `user_id`: uuid, foreign key to auth.users(id)
   - `name`: text, not null
   - `token`: text, not null, unique
   - `created_at`: timestamptz, default: now()
   - `last_used`: timestamptz, nullable
   - `is_active`: boolean, default: true
4. **Enable RLS** and add policies for user access

### 🔐 Security Note
For the MVP, we're storing actual tokens (not hashed) for simplicity. In production, you should:
- Store hashed tokens in the database
- Only return the actual token once when generated
- Implement proper token rotation and expiration

### 📞 Still Having Issues?
If you're still seeing the error after following these steps:
1. Check browser console for specific error messages
2. Verify your Supabase project URL and API keys are correct
3. Ensure you're authenticated (signed in) when generating tokens
4. Check the Network tab to see the actual API request/response

### 🎯 Expected Result
After fixing the schema, you should see:
- ✅ "Token generated successfully!" message
- ✅ Token appears in the dashboard list
- ✅ Token can be copied and used
- ✅ No console errors

### 📋 What Changed
**Migration Simplified**: The original migration files have been merged into a single `001_initial_schema.sql` file that creates the correct schema from the start, matching frontend expectations. 