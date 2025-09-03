#!/bin/bash

echo "🛑 Stopping Corpus AI Companion..."

# Kill known services by pattern
pkill -f "python.*capabilities/speech/app_swagger.py" 2>/dev/null
pkill -f "python.*capabilities/vision/app_swagger.py" 2>/dev/null
pkill -f "python.*orchestrator/main_pipeline_swagger.py" 2>/dev/null

# Extra safety: free known ports (Speech 5001, Vision 5002, Orchestrator 5000, Raw WS 5010)
for port in 5001 5002 5000 ${LOG_WS_PORT:-5010}; do
  sudo fuser -k $port/tcp 2>/dev/null || true
done

echo "✅ All processes stopped"

