#!/bin/bash

# Start Frontend Development Server
echo "🚀 Starting TEMPO Air Quality Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found. Please run this script from the project root."
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local file..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

# Start development server
echo "🌟 Starting development server on http://localhost:3000"
npm run dev
