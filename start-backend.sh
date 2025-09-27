#!/bin/bash

# Start Backend Development Server
echo "🚀 Starting TEMPO Air Quality Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Navigate to backend directory
cd backend

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Please run this script from the project root."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "⚠️  Please update .env file with your API keys"
fi

# Start development server
echo "🌟 Starting development server on http://localhost:8000"
echo "📚 API documentation available at http://localhost:8000/docs"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
