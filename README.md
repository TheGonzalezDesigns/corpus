# Corpus - Raspberry Pi AI Companion

A modular AI companion system for Raspberry Pi that provides comprehensive sensory and cognitive capabilities.

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

## Status

🚧 **In Development** - Starting with speech capabilities

## Hardware Requirements

- Raspberry Pi 4+ (recommended)
- Camera module (for vision)
- USB microphone or audio HAT (for audio input)
- Speakers or audio HAT (for speech output)
- Optional: Additional sensors, servo controllers, etc.