#!/bin/bash

# Start Both Frontend and Backend
echo "🚀 Starting TEMPO Air Quality App..."

# Function to start backend
start_backend() {
    echo "🔧 Starting backend..."
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        cp env.example .env
        echo "⚠️  Please update .env file with your API keys"
    fi
    
    # Start backend in background
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "✅ Backend started with PID $BACKEND_PID"
    
    cd ..
}

# Function to start frontend
start_frontend() {
    echo "🔧 Starting frontend..."
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing dependencies..."
        npm install
    fi
    
    # Create .env.local if it doesn't exist
    if [ ! -f ".env.local" ]; then
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    fi
    
    # Start frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ Frontend started with PID $FRONTEND_PID"
    
    cd ..
}

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start services
start_backend
sleep 5  # Wait for backend to start
start_frontend

echo "🌟 TEMPO Air Quality App is running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait
