#!/bin/bash

set -e

echo "🚀 Deploying DhafnckMCP Frontend to Vercel..."

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Must be run from the project root directory"
    exit 1
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Navigate to frontend directory
cd frontend

# Check if .env.local exists, if not create from example
if [ ! -f ".env.local" ]; then
    echo "⚠️  No .env.local found. Please set up your environment variables:"
    echo "   1. Copy env.example to .env.local"
    echo "   2. Add your Supabase URL and anon key"
    echo "   3. Run this script again"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Build the application
echo "🔨 Building application..."
npm run build

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
if [ "$1" = "--production" ]; then
    echo "🌟 Deploying to PRODUCTION..."
    vercel --prod --yes
else
    echo "🧪 Deploying to PREVIEW..."
    vercel --yes
fi

echo "✅ Frontend deployment completed!"
echo "🌐 Your application should be available at the URL provided by Vercel" 