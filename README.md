# Corpus - Raspberry Pi AI Companion

A modular AI companion system for Raspberry Pi that provides comprehensive sensory and cognitive capabilities.

**⚠️ EARLY ALPHA** — Moderate tracking and description capabilities; active development.

Theory (what’s new and why)
- Event windows: Instead of speaking on every frame, the system aggregates rapid triggers into a single 4s (max) window and summarizes once. This reduces repetition and yields coherent, human-friendly speech.
- Event memory: Each aggregated window is persisted as a compact JSONL record (ts, duration, frames_count, description). These curated logs act as short-term “memory” for context in future prompts.
- Provider routing: Vision description can use Gemini, OpenAI, or Claude. The router tries providers in a configurable, cost-aware order (default: gemini,openai,claude) and falls back automatically on errors.
- Live telemetry: Vision exposes a dedicated raw WebSocket on a separate port for real-time events (waldo_event, waldo_log, waldo_state, api, stats).

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

New in this alpha
- Aggregated event windows (debounced vision) with single summary + speech
- Event memory store (JSONL) + query endpoints for recent/range/context
- Provider routing with automatic failover (Gemini → OpenAI → Claude)
- Live event logs via raw WebSocket: `ws://<host>:5010` (configurable `LOG_WS_PORT`)
- Orchestrator capability probe: `POST /capabilities/check`

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
- Persist time-stamped “event windows” as context for later prompts

What you’ll see at startup
- Service health confirmations for Speech, Vision, Orchestrator
- Ingest auto-start and connection check (up to ~20s)
  - Example: `✅ Ingest connected to wss://dev.thegonzalez.design/ws/ingest/pi (sent=N)`
  - If it can’t connect, a clear warning prints but everything else keeps running
- Per-frame logs once connected: `Ingest: sent frame #N (X bytes)`

WebSocket streams
- Raw log hub: `ws://<host>:5010` (configurable via `LOG_WS_PORT`)
- Periodic ingest heartbeat (every ~2s) with `type=ingest_digest` including: `connected`, `sent_count`, `queue_size`, `url`, `last_error`, `ts`

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

Notes & Caveats (Alpha)
- Speech summarization is debounced: bursts are summarized once per window and spoken once.
- Event memory is an on-disk JSONL file for local context; consider log rotation/retention for long runs.
- Provider routing requires corresponding API keys in `.env` (GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY);
  order is set via `VISION_PROVIDER_ORDER`.
- The raw WebSocket uses `websockets` in-process; it’s intended for dashboards/CLI streaming.
 - Ingest is always-on by default and will attempt to connect automatically to the configured URL.

## Environment (.env)

Defaults are provided so it “just works.” The repo ships with a pre-set ingest URL to the dev EC2 endpoint.

Required:
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`

Optional:
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` (provider router)
- `HUME_API_KEY` (primary TTS; falls back automatically when exhausted)
- `INGEST_WS_URL` (WebSocket to stream frames; defaults to dev EC2 and can be changed)

Tip: You can change ingest at runtime via the Vision API:
```
curl -s -H 'Content-Type: application/json' \
  -X POST http://localhost:5002/ingest/config \
  -d '{"url":"wss://your.server/ws/ingest/pi"}'
```

## Startup and Shutdown

- Start everything: `./start_corpus.sh`
  - Preflight + API health checks, camera config, voice selection
  - Forces ingest to start and confirms connection within ~20s
- Stop everything: `./stop_corpus.sh`
  - Stops Speech, Vision, Orchestrator, monitoring, ingest, and WS hubs; frees ports

## Vision API (Swagger)

- `http://raspberrypi:5002/swagger`
- Ingest endpoints:
  - `GET /ingest/status` — connection state and counters
  - `POST /ingest/start` — start ingest and enable WS digest
  - `POST /ingest/stop` — stop ingest and WS digest
  - `POST /ingest/config` — set url at runtime; auto-restarts ingest

New in this alpha:
- **Provider routing** for vision (Gemini → OpenAI → Claude) with automatic failover
- **Live event logs** via WebSocket: `ws://<host>:5010` (raw JSON stream)
- **Capability probe** endpoint in orchestrator: `POST /capabilities/check`
- **Stability fixes** in Waldo filter (RGBA pipeline)
