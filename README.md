# Corpus - Raspberry Pi AI Companion

A modular AI companion system for Raspberry Pi that provides comprehensive sensory and cognitive capabilities.

**⚠️ EARLY ALPHA** — Moderate tracking and description capabilities; active development.

## Overview

Corpus is designed as a distributed system where each major capability is implemented as a separate repository, allowing for independent development and deployment while maintaining a cohesive overall experience.

## Architecture

The system consists of the main orchestration layer (this repo) and specialized capability modules:

### Core Capabilities
- **Eyes** (Vision) - Computer vision processing and object recognition
- **Ears** (Audio Input) - Audio capture, processing, and speech recognition  
- **Mouth** (Speech Output) - Text-to-speech synthesis and audio output
- **Brain** (AI Processing) - Central intelligence, decision making, and coordination
- **Wings** (Mobility) - Future drone/movement capabilities

### Repository Structure
```
corpus/                    # Main orchestration repo (this repo)
├── corpus-speech/         # Speech synthesis and audio output
├── corpus-vision/         # Computer vision and image processing
├── corpus-audio/          # Audio input and speech recognition
├── corpus-brain/          # AI processing and decision making
└── corpus-wings/          # Movement and drone capabilities (future)
```

## Getting Started

1. Clone this repository and the required capability modules
2. Follow setup instructions for each capability
3. Configure the main orchestration system
4. Launch the integrated system

## Integration

Each capability module exposes standardized APIs that the main system coordinates. Communication between modules uses [TBD - message queues/REST APIs/gRPC].

## Current Status

✅ Current Alpha Capabilities:
- **Emotional Speech**: Hume TTS with 101+ voice personalities  
- **Intelligent Vision**: Waldo Vision multi-layer scene analysis
- **Event-driven Responses**: Automatic reactions to environmental changes
- **Cost-optimized**: 95%+ API savings through smart filtering
- **One-command startup**: `./start_corpus.sh`

## 🚀 Quick Start

```bash
# Clone and start everything
git clone --recursive https://github.com/TheGonzalezDesigns/corpus.git
cd corpus
./start_corpus.sh
```

**Your AI companion will:**
- Watch continuously through camera
- Speak automatically when significant changes occur  
- Respond with genuine emotion and personality
- Save costs through intelligent filtering

## Hardware Requirements

### ✅ **Tested Configuration:**
- **Raspberry Pi 4** with Raspberry Pi OS
- **Logitech BRIO 4K Webcam** (USB)
- **Audio output** (3.5mm, HDMI, or USB speakers)
- **Internet connection** (for Hume TTS and Gemini AI)

### 🎛️ **Camera Support:**
- Any USB camera supported by OpenCV
- Optimal: 640×480 @ 30fps for real-time processing
- Waldo Vision auto-configures to camera capabilities

New in this alpha:
- **Provider routing** for vision (Gemini → OpenAI → Claude) with automatic failover
- **Live event logs** via WebSocket: `ws://<host>:5010` (raw JSON stream)
- **Capability probe** endpoint in orchestrator: `POST /capabilities/check`
- **Stability fixes** in Waldo filter (RGBA pipeline)
