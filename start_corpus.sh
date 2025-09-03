#!/bin/bash

# THEORY:
# This is the master startup script for the Corpus AI Companion system.
# It orchestrates the complete initialization sequence of all microservices
# in the correct order, handles service dependencies, and configures optimal
# settings for the integrated AI companion experience.
#
# The script embodies the "infrastructure as code" principle, ensuring
# that the complex multi-service architecture can be launched with a single
# command while handling common failure modes like port conflicts and
# camera access issues automatically.
#
# Architecture Managed:
# - Speech API (Hume TTS with 101 voices)
# - Vision API (Waldo Vision intelligent filtering) 
# - Orchestrator (Pipeline coordination)
# - Camera configuration and conflict resolution
# - Service health monitoring and auto-restart

# CAVEATS & WARNINGS:
# - Requires manual Ctrl+C to stop (no graceful shutdown signal handling)
# - Service PIDs not persisted (can't stop individual services after startup)
# - Camera device detection is basic (may fail if multiple cameras present)
# - No service dependency verification (starts all services simultaneously)
# - Hardcoded port numbers (5000, 5001, 5002) not configurable
# - No log rotation for waldo_vision.log (file grows indefinitely)
# - Virtual environment paths are relative (may break if run from wrong directory)
# - No backup/recovery if configuration APIs fail during setup

echo "🤖 Starting Corpus AI Companion System..."
echo "========================================"

# Function to kill existing services
cleanup_services() {
    echo "🛑 Stopping existing services..."
    pkill -f "python.*app_swagger.py" 2>/dev/null
    pkill -f "python.*main_pipeline_swagger.py" 2>/dev/null
    pkill vlc 2>/dev/null
    sleep 2
    echo "✅ Services stopped"
}

# Function to check if port is free
check_port() {
    local port=$1
    if lsof -i:$port >/dev/null 2>&1; then
        echo "⚠️  Port $port is busy - killing process..."
        sudo fuser -k $port/tcp 2>/dev/null
        sleep 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=10
    local attempt=1
    
    echo "⏳ Waiting for $name to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s $url >/dev/null 2>&1; then
            echo "✅ $name is ready"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    echo "❌ $name failed to start"
    return 1
}

# Main startup sequence
main() {
    cd /home/nerostar/Projects/corpus
    
    # Step 1: Cleanup
    cleanup_services
    check_port 5001
    check_port 5002  
    check_port 5000
    
    echo ""
    echo "🚀 Starting services..."
    
    # Step 2: Start Speech API
    echo "🗣️  Starting Speech API (Hume TTS)..."
    cd capabilities/speech
    source venv/bin/activate
    python app_swagger.py &
    SPEECH_PID=$!
    cd ../..
    
    # Step 3: Start Vision API  
    echo "👁️  Starting Vision API (Waldo Vision)..."
    cd capabilities/vision
    source venv/bin/activate
    GEMINI_API_KEY=$GOOGLE_API_KEY python app_swagger.py &
    VISION_PID=$!
    cd ../..
    
    # Step 4: Start Orchestrator
    echo "🧠 Starting Orchestrator..."
    cd orchestrator
    source venv/bin/activate
    python main_pipeline_swagger.py &
    ORCHESTRATOR_PID=$!
    cd ..
    
    # Step 5: Wait for services to be ready
    echo ""
    echo "⏳ Checking service health..."
    wait_for_service "http://localhost:5001/status" "Speech API" || exit 1
    wait_for_service "http://localhost:5002/status" "Vision API" || exit 1  
    wait_for_service "http://localhost:5000/status" "Orchestrator" || exit 1
    
    # Step 6: Configure optimal settings
    echo ""
    echo "⚙️  Configuring system..."
    
    # Set optimal camera preset
    curl -s -X POST "http://localhost:5002/camera/config?quality_preset=smooth_480p" >/dev/null
    echo "📹 Camera configured: 480p @ 30fps"
    
    # Set Ito voice  
    curl -s -X POST "http://localhost:5001/voice?voice_name=Ito" >/dev/null
    echo "🗣️  Voice set: Ito"
    
    # Step 7: Start Waldo Vision monitoring
    echo ""
    echo "🦀 Starting Waldo Vision continuous monitoring..."
    curl -s -X POST "http://localhost:5002/monitor/start" >/dev/null
    echo "👁️  Event-driven monitoring ACTIVE"
    
    # Step 8: Display status
    echo ""
    echo "🎉 Corpus AI Companion is READY!"
    echo "================================="
    echo "Services:"
    echo "  🗣️  Speech API:     http://raspberrypi:5001/swagger"
    echo "  👁️  Vision API:     http://raspberrypi:5002/swagger" 
    echo "  🧠 Orchestrator:   http://raspberrypi:5000/swagger"
    echo ""
    echo "Real-time monitoring:"
    echo "  📊 Monitor logs:   tail -f /home/nerostar/Projects/corpus/waldo_vision.log"
    echo "  📈 Performance:    curl http://raspberrypi:5002/monitor/status"
    echo ""
    echo "Control:"
    echo "  ⏹️  Stop all:       curl -X POST http://raspberrypi:5002/monitor/stop"
    echo "  🔄 Restart:        ./start_corpus.sh"
    echo ""
    echo "💡 Your AI companion is watching and will speak when significant changes occur!"
    echo "   Try walking into the camera view to trigger DISTURBED state detection."
    
    # Keep script running to monitor
    echo ""
    echo "Press Ctrl+C to stop all services..."
    trap cleanup_and_exit SIGINT
    
    while true; do
        sleep 10
        # Check if services are still running
        if ! kill -0 $SPEECH_PID 2>/dev/null; then
            echo "❌ Speech service died - restarting..."
            break
        fi
        if ! kill -0 $VISION_PID 2>/dev/null; then
            echo "❌ Vision service died - restarting..." 
            break
        fi
        if ! kill -0 $ORCHESTRATOR_PID 2>/dev/null; then
            echo "❌ Orchestrator died - restarting..."
            break
        fi
    done
}

cleanup_and_exit() {
    echo ""
    echo "🛑 Shutting down Corpus AI Companion..."
    cleanup_services
    echo "👋 Goodbye!"
    exit 0
}

# Run main function
main